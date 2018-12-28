from logging import *
from logging.config import fileConfig, dictConfig
import os
import json
from collections import OrderedDict

dir_path = os.path.dirname(os.path.realpath(__file__))
log_path = os.path.join(dir_path, '../ci-output/script-logs')
log_file = os.path.join(log_path, 'logs.log')
log_ini_file = os.path.join(dir_path, 'log.ini')

def get_list(filename):
	with open(filename, 'r', encoding='iso-8859-1') as f:
		lines = f.read().splitlines()
		lines = [l for l in lines if not l.startswith('#')]
		return lines

class SlackHandler(Handler):
    def __init__(self, *args, **kwargs):
        super(SlackHandler, self).__init__(*args, **kwargs)
        self.buffer = []
        self.slack_url = self.get_environment_variable('SLACK_TOKEN')
        self.details = {
            'commit' : self.get_environment_variable('CI_COMMIT_SHA'),
            'message': self.get_environment_variable('CI_COMMIT_MESSAGE'),
            'user'   : self.get_environment_variable('GITLAB_USER_NAME'),
            'user-email' : self.get_environment_variable('GITLAB_USER_EMAIL'),
            'job-URL': self.get_environment_variable('CI_JOB_URL')
        }
        if self.details['message'] is not None:
            self.details['message'] = self.details['message'].rstrip()
        for k in list(self.details.keys()):
            if self.details[k] is None:
                del self.details[k]
                
        # parse slack user IDs
        self.slack_id_dict = {}
        slack_ids_file = os.path.join(dir_path, 'slack-user-ids.txt')
        ids_list = get_list(slack_ids_file)
        for d in ids_list:
            splits = d.split(",")
            email = splits[0]
            slack_id = splits[1]
            self.slack_id_dict[email] = slack_id
        
    def get_environment_variable(self, name):
        return os.environ.get(name, None)

    def emit(self, record):
        msg = self.format(record)
        logger.debug('Slack message: %s', msg)
        self.buffer.append(msg)

    def post_to_slack(self, msg):
        if self.slack_url is None:
            logger.info('Not sending message to slack because slack url is not set...')

        else:
            logger.info('Sending message to slack...')

            payload = json.dumps({'text': msg})
            logger.debug('Sending payload to slack %s: %s', self.slack_url, payload)
            r = requests.post(self.slack_url, data=payload, headers={'Content-Type': 'application/json'})
            logger.debug("Slack Response: %s %s", r.status_code, r.text.encode('utf-8'))
            
    def format_slack_mention(self, user_email):
        if user_email in self.slack_id_dict:
            return "<@%s>" % self.slack_id_dict[user_email]
        return ""

    def flush(self):
        if len(self.buffer) > 0:
            labels = OrderedDict([
                ('commit', 'Commit'),
                ('message', 'Commit message'),
                ('user', 'Who'),
                ('job-URL', 'Details')
            ])
            details = ['> ' + l + ': ' + self.details[k] for k, l in labels.items() if k in self.details]
            context = 'The latest commit contains errors. Please fix them. ' + '\n' + '\n'.join(details)
            if "user-email" in self.details:
            	context =  self.format_slack_mention(self.details["user-email"]) + ' ' + context

            msgs = '\n\n'.join([context] + self.buffer)
            self.post_to_slack(msgs)
            self.buffer = []


fileConfig(log_ini_file, defaults={'logfile': log_file})
logger = getLogger('sLogger')


def report_error(error, details=None, solutions=None):
    """
    :param error: string
    :param details: list of strings
    :param solutions: list of strings
    """
    # details
    if details is not None:
        details = ['> ' + s for s in details]
        details = ['[DETAILS]:'] + details
        details = '\n'.join(details)
    # solutions
    if solutions is not None:
        solutions = ['> ' + s for s in solutions]
        solutions = ['[SOLUTIONS]:'] + solutions
        solutions = '\n'.join(solutions)
    msg = '[ERROR]: ' + error
    if details is not None:
        msg += '\n' + details
    if solutions is not None:
        msg += '\n' + solutions
    logger.error(msg)
