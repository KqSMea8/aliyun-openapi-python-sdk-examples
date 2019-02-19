#encoding=utf-8
import sys
import json

from aliyunsdkcore.acs_exception.exceptions import ServerException, ClientException
from sdk_lib.consts import *
from aliyunsdkslb.request.v20140515 import CreateLoadBalancerRequest
from aliyunsdkslb.request.v20140515 import DeleteLoadBalancerRequest
from sdk_lib.exception import ExceptionHandler
from sdk_lib.common_util import CommonUtil

client = ACS_CLIENT

'''
创建slb实例->删除slb实例
'''

def create_load_balancer():
    '''
    create_load_balancer：创建slb实例
    官网API参考链接：https://help.aliyun.com/document_detail/27577.html
    '''
    try:
        request = CreateLoadBalancerRequest.CreateLoadBalancerRequest()
        response = client.do_action_with_exception(request)

        response_json = json.loads(response)
        return response_json
    except ServerException as e:
        ExceptionHandler.server_exception(e)
    except ClientException as e:
        ExceptionHandler.client_exception(e)

def delete_load_balancer(load_balancer_id):
    '''
    delete_load_balancer：删除slb实例
    官网API参考链接：https://help.aliyun.com/document_detail/27579.html
    '''
    try:
        request = DeleteLoadBalancerRequest.DeleteLoadBalancerRequest()
        #负载均衡实例的ID
        request.set_LoadBalancerId(load_balancer_id)
        response = client.do_action_with_exception(request)
        response_json = json.loads(response)
        return response_json
    except ServerException as e:
        ExceptionHandler.server_exception(e)
    except ClientException as e:
        ExceptionHandler.client_exception(e)

def main():

    #创建slb实例
    load_balancer_json = create_load_balancer()
    CommonUtil.log("create_load_balancer", load_balancer_json)

    #删除slb实例
    load_balancer_json = delete_load_balancer(load_balancer_json["LoadBalancerId"])
    CommonUtil.log("delete_load_balancer", load_balancer_json)


if __name__ == "__main__":
    sys.exit(main())