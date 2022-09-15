#!/usr/bin/env python3

import argparse
import json
import requests
import time
import logging

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

SCRIPT_VERSION = 'v1.1.0'
HTTP_TIMEOUT = 10
HTTP_VERIFY_SSL = False
SLEEP_TIME = 30
MAX_WAIT_TIME = 600

class RunCLI(object):
  # -----------------------------------------------------------------
  # run me
  def __init__(self):
    # parse cmd arguments
    self.read_cli_args()
    if self.args.log_level == "DEBUG":
      logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)
    else:
      logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)

    # create jobs
    tasks = self.nobod_ci_create_job()
    if tasks is None:
      logging.error('Failed to create CI jobs in NOBOD')
      exit(1)
    # logging.info(json.dumps(tasks, indent=2, sort_keys=True))
    
    # verify response
    if 'jobs' not in tasks:
      logging.error('No instances found')
      exit(1)

    # go thru all tasks and wait for finishing
    exitcode = 0
    for task in tasks.get('jobs'):
      jobId = task.get('job')
      exitcode += self.nobod_ci_wait_for_job(jobId)

    exit(exitcode)

  # -----------------------------------------------------------------
  # wait for jobs
  def nobod_ci_wait_for_job(self, jobId):
    loop = 0
    exitcode = 0
    while True:
      if loop*SLEEP_TIME > self.args.job_finish_timeout:
        logging.error('Job did not respond within {} seconds'.format(self.args.job_finish_timeout))
        exitcode = 1
        break

      job = self.nobod_ci_get_job(jobId)
      
      if job is None:
        exitcode = 1
        logging.error('Job {} not found'.format(jobId))
        break
      
      finished = job.get('finished')
      if finished is not None:
        exitcode = job.get('job_returncode')
        result = json.loads(job.get('job_result'))

        if exitcode == 0:
          status = 'successful'
        else:
          status = 'failed'
        
        logging.info('Job {} finished with state {}.\nOutput:\n{}'.format(jobId, status, json.dumps(result, indent=1)))
        break

      logging.info('Waiting {} seconds ...'.format(self.args.job_wait_timeout))
      time.sleep(self.args.job_wait_timeout)
      loop += 1

    return exitcode

  # -----------------------------------------------------------------
  # create ci jobs
  def nobod_ci_get_job(self, jobId):
    url = self.args.url + "/api/job/" + jobId
    username = self.args.username
    password = self.args.password

    headers = dict()
    headers['Accept'] = 'application/json'
    headers['User-Agent'] = 'acoby-nobod-ci-script/'+SCRIPT_VERSION
    headers['Connection'] = 'close'

    logging.info('Calling: GET {}'.format(url))

    try:
      result = requests.get(url, timeout=self.args.http_timeout, auth=(username,password), headers=headers, verify=self.args.tls_verify)
      if result.status_code == 200:
        result.encoding = 'utf-8'
        return json.loads(result.text)

      return None
    except BaseException as err:
      logging.error('Could not read CI response from NOBOD.\n{}'.format(err))
      exit(1)
  
  # -----------------------------------------------------------------
  # create ci jobs
  def nobod_ci_create_job(self):
    url = self.args.url + "/api/job/ci?qualifier=" + self.args.qualifier
    
    if self.args.instance != None:
      url = url + "&instance=" + self.args.instance
    
    username = self.args.username
    password = self.args.password
    
    headers = dict()
    headers['Accept'] = 'application/json'
    headers['Content-Type'] = 'application/json'
    headers['User-Agent'] = 'acoby-nobod-ci-script/'+SCRIPT_VERSION
    headers['Connection'] = 'close'
    
    logging.debug('Calling: POST {}'.format(url))
    
    try:
      result = requests.post(url, timeout=self.args.http_timeout, auth=(username,password), headers=headers, verify=self.args.tls_verify)
      if result.status_code == 200:
        result.encoding = 'utf-8'
        return json.loads(result.text)
      else:
        logging.error('Got wrong response code {} with body {}'.format(result.status_code, result))

      return None
    except BaseException as err:
      logging.error('Could not read CI response from NOBOD.\n{}'.format(err))
      exit(1)

  # -----------------------------------------------------------------
  # Read the command line args passed to the script.
  def read_cli_args(self):
    parser = argparse.ArgumentParser()
    parser.add_argument('--qualifier', action = 'store', type=str, help='qualifier for a service', required=True)
    parser.add_argument('--url', action = 'store', type=str, help='an URL to the NOBOD CI API', required=True)
    parser.add_argument('--username', action = 'store', type=str, help='the username to access the NOBOD CI API', required=True)
    parser.add_argument('--password', action = 'store', type=str, help='the password to access the NOBOD CI API', required=True)
    parser.add_argument('--instance', action = 'store', type=str, help='an optional concrete instance id', required=False)
    parser.add_argument('--job-wait-timeout', action = 'store', type=int, help='an optional concrete wait time in seconds', required=False, default=SLEEP_TIME)
    parser.add_argument('--job-finish-timeout', action = 'store', type=int, help='wait for that time within the job should finish', required=False, default=MAX_WAIT_TIME)
    parser.add_argument('--tls-verify', action = 'store', type=bool, help='check a valid TLS connection', required=False, default=HTTP_VERIFY_SSL)
    parser.add_argument('--http-timeout', action = 'store', type=int, help='wait for that time for the API', required=False, default=HTTP_TIMEOUT)
    parser.add_argument('--log-level', action = 'store', type=str, help='defines the log level', required=False, default="INFO", choices=["DEBUG","INFO"])
    self.args = parser.parse_args()

# Run the tool
RunCLI()
