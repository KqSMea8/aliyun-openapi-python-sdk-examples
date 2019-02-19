#encoding=utf-8
import sys
import json

from aliyunsdkcore.acs_exception.exceptions import ServerException, ClientException
from sdk_lib.consts import *
from sdk_lib.common_util import CommonUtil
from sdk_lib.exception import ExceptionHandler
from aliyunsdkslb.request.v20140515 import DescribeLoadBalancerAttributeRequest
from aliyunsdkslb.request.v20140515 import CreateLoadBalancerRequest
from sdk_lib.sdk_load_balancer import LoadBalancer
from sdk_lib.sdk_tcp_listener import TcpListener

'''
创建slb实例->添加tcp监听->查询slb实例->slb实例克隆->删除slb实例
'''

client = ACS_CLIENT

#查询slb实例
def describe_load_balancer_attribute(params):
    '''
    describe_load_balancer_attribute：查询指定负载均衡实例的详细信息
    官网API参考链接: https://help.aliyun.com/document_detail/27583.html
    '''
    counter = 0
    while counter < TRY_TIME:
        try:
            request = DescribeLoadBalancerAttributeRequest.DescribeLoadBalancerAttributeRequest()
            #负载均衡实例的id
            request.set_LoadBalancerId(params["load_balancer_id"])
            response = client.do_action_with_exception(request)
            response_json = json.loads(response)
            return response_json
        except ServerException as e:
            ExceptionHandler.server_exception(e)
        except ClientException as e:
            ExceptionHandler.client_exception(e)
        finally:
            counter += 1

#创建slb实例
def create_load_balancer(params):
    '''
    create_load_balancer：创建slb实例
    官网API参考链接：https://help.aliyun.com/document_detail/27577.html
    '''
    counter = 0
    while counter < TRY_TIME:
        try:
            request = CreateLoadBalancerRequest.CreateLoadBalancerRequest()
            #公网类型实例的付费方式
            request.set_LoadBalancerName(params["LoadBalancerName"])
            response = client.do_action_with_exception(request)
            response_json = json.loads(response)
            return response_json
        except ServerException as e:
            ExceptionHandler.server_exception(e)
        except ClientException as e:
            ExceptionHandler.client_exception(e)
        finally:
            counter += 1


def main():
    load_balancer = LoadBalancer(client)
    tcp_listener = TcpListener(client)
    params = {}
    params["bandwidth"] = BANDWIDTH_NOT_LIMITED
    params["listener_port"] = 443
    params["backend_server_port"] = 443

    #创建slb实例
    load_balancer_json = load_balancer.create_load_balancer()
    CommonUtil.log("create_load_balancer", load_balancer_json)

    params["load_balancer_id"] = load_balancer_json["LoadBalancerId"]
    params["LoadBalancerName"] = load_balancer_json["LoadBalancerName"]

    #添加tcp监听
    result_json = tcp_listener.create_tcp_listener(params)
    CommonUtil.log("create_tcp_listener", result_json)

    #查询slb实例
    result_json = describe_load_balancer_attribute(params)
    CommonUtil.log("describe_load_balancer_attribute", result_json)

    #创建slb实例
    result_json = create_load_balancer(params)
    CommonUtil.log("create_load_balancer", result_json)

    #删除slb实例
    result_json = load_balancer.delete_load_balancer(params)
    CommonUtil.log("delete_load_balancer", result_json)


if __name__ == "__main__":
    sys.exit(main())