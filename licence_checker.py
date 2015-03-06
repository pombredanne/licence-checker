__author__ = 'mantjonu'

from github import Github
from multiprocessing import Pool
from datetime import datetime

startTime = datetime.now()

# git login, password
git = Github('login', 'password')
organization = 'ongr-io'


do_not_check = ['raimundas/NFQ-projektas-Muziej-populiarinimas-.', 'chyzas/Week1', 'chyzas/Week2',
                'ongr-io/ongr-strict-standard', 'chyzas/LearningStuff2', 'chyzas/kapietums', 'chyzas/IcyFood']

# refs = ['master', 'tag']  # will be used later. If needed
#
# def get_repository_refs(repo):
#     """
#     Returns all refs from repository. Will be used later if needed.
#     :param repo: repository
#     :return: list
#     """
#     data = {}
#     references = git.get_repo(repo).get_git_refs()._fetchNextPage()
#     data[repo] = [i.ref[5:] for i in references if any(string in i.ref for string in refs)]
#     return data


def read_file(file):
    with open(file, 'r') as f:
        return f.read()

licence_data = read_file('licence.txt')


def threads(func, list_items, thread_qty):
    """
    :param func: worker function
    :param list_items: items to worker
    :param thread_qty: threads quantity
    :return:
    """
    pool = Pool(thread_qty)
    jobs = []
    job_count = 0
    for job in pool.imap_unordered(func, list_items):
        jobs.append(job)
        job_count += 1
        incomplete = len(list_items) - job_count
        unsubmitted = max(0, incomplete - thread_qty)
        print "Jobs incomplete: {0}. Unsubmitted: {1}".format(incomplete, unsubmitted)
    pool.close()
    pool.join()
    return jobs


def get_all_repositories():
    return [i.full_name for i in git.get_organization(organization).get_repos() if i.full_name not in do_not_check]


def get_repositories_sha(repositories):
    """
    :param repositories: all respositories
    :return: array of dict containing repo and sha
    """
    data = []
    for repo in repositories:
        temp = {}
        try:
            repository = git.get_repo(repo)
            raw_data = repository.get_git_ref('heads/master')
            sha = raw_data.object.sha
            temp[repo] = sha
            data.append(temp)
        except Exception:
            print repo

    return data


def check_licences(data):
    """
    Checks licences. Thread function.
    :param data: data from
    """
    repo = data.keys()[0]
    sha = data.values()[0]
    repository = git.get_repo(repo)
    repository_tree = repository.get_git_tree(sha, recursive=True).tree
    paths = [i.path for i in repository_tree]
    count_paths = len(paths)
    for nr, path in enumerate(paths):
        if path.endswith('php'):
            raw_data = repository.get_contents(path).raw_data
            content = raw_data.get('content').decode('base64')
            print "checking {}: {}, left {}".format(repo, path, count_paths - nr)
            if not licence_data in content:
                html_url = raw_data.get('html_url')
                info = "{}: {} \n".format(repo, html_url)
                with open('wrong_licence.txt', 'a') as f:
                    f.write(info)

all_data = get_repositories_sha(get_all_repositories())

print all_data
threads(check_licences, all_data, 5)

print (datetime.now()-startTime)
