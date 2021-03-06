#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .services import CodeMetricService
from .exceptions import RepoIDNotFound
from codemetric.settings import SETTING_MANAGE_URL

import json
import logging
import requests


@api_view(['GET'])
def get_codebase_gpa(request):
    """
    Gets the codebase's current GPA from Codeclimate.
    """
    logging.info('Get codebase GPA')
    instance_id = request.GET.get('instance_id')
    user_email = request.GET.get('user_email')
    github_user = request.GET.get('github_user')
    github_repo = request.GET.get('github_repo')

    if instance_id is None or len(instance_id) <= 0:
        logging.warn('Missing instance ID')
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if github_user is None or len(github_user.strip()) <= 0:
        logging.warn('Missing Github username')
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Need to specify github_user")

    if github_repo is None or len(github_repo.strip()) <= 0:
        logging.warn('Missing github_repo')
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Need to specify github_repo")

    try:
        # Fetch github token from settingmanage
        params = {'instance_id': instance_id, 'user_email': user_email}
        r = requests.get(SETTING_MANAGE_URL + "v1/tokenstorage/", params=params)

        github_api_token = r.json()['github_token']
        codemetric_service = CodeMetricService(github_token=github_api_token)

        repo_id = codemetric_service.retrieve_repo_id_using_repo_name(github_user + "/" + github_repo)

        data = {
            'user': github_user,
            'repo_name': github_repo,
            'repo_id': repo_id,
        }

        if repo_id is None or len(repo_id) <= 0:
            data['gpa'] = '-1'
            return Response(data=json.dumps(data),
                            status=status.HTTP_404_NOT_FOUND,
                            content_type="application/json")

        codebase_gpa = codemetric_service.get_codebase_gpa(repo_id)

        data['gpa'] = codebase_gpa

        return Response(data=json.dumps(data),
                        content_type="application/json",
                        status=status.HTTP_200_OK)

    except ValueError as e:
        logging.warn(e)
        raise RepoIDNotFound

    except Exception as e:
        logging.error(e)
        return Response(data=e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_test_coverage_history(request):
    """
    Returns test coverage history collected by Codeclimate.
    """
    logging.info('Attempting to retrieve coverage history...')
    instance_id = request.GET.get('instance_id')
    user_email = request.GET.get('user_email')
    github_user = request.GET.get('github_user')
    github_repo = request.GET.get('github_repo')

    if instance_id is None or len(instance_id) <= 0:
        logging.warn('Missing instance ID')
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    try:
        # Fetch github token from settingmanage
        params = {'instance_id': instance_id, 'user_email': user_email}
        r = requests.get(SETTING_MANAGE_URL + "v1/tokenstorage/", params=params)

        github_api_token = r.json()['github_token']
        codemetric_service = CodeMetricService(github_token=github_api_token)

        repo_id = codemetric_service.retrieve_repo_id_using_repo_name(repo_name="{}/{}".format(github_user,
                                                                                               github_repo))

        data = {
            'user': github_user,
            'repo_name': github_repo,
            'repo_id': repo_id,
        }

        test_coverage_history = codemetric_service.get_test_coverage_history(repo_id=repo_id)

        if test_coverage_history is None or len(test_coverage_history) <= 0:
            data['coverage-history'] = []
            return Response(data=json.dumps(data),
                            status=status.HTTP_200_OK,
                            content_type="application/json")

        data['coverage-history'] = test_coverage_history
        return Response(data=data,
                        status=status.HTTP_200_OK,
                        content_type="application/json")

    except ValueError as e:
        logging.warn(e)
        raise RepoIDNotFound

    except Exception as e:
        print("Something unexpected happened")
        logging.error(e)
        return Response(data=e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def hello_world(request):
    """
    Returns hello world - this is only to test if the application is serving any incoming traffic.
    """
    return Response(data="hello", content_type="text/plain")
