#encoding=utf-8
import json
import sys

from aliyunsdkcore.acs_exception.exceptions import ServerException, ClientException
from aliyunsdkslb.request.v20140515 import AddBackendServersRequest
from aliyunsdkslb.request.v20140515 import CreateLoadBalancerTCPListenerRequest
from aliyunsdkslb.request.v20140515 import RemoveBackendServersRequest

from sdk_lib.common_util import CommonUtil
from sdk_lib.consts import *
from sdk_lib.exception import ExceptionHandler
from sdk_lib.sdk_load_balancer import LoadBalancer

'''
创建slb实例->添加后端服务器->创建tcp监听->删除后端服务器->删除slb实例
'''
client = ACS_CLIENT


def add_backend_servers(params):
    '''
    add_backend_servers：添加后端服务器
    官网API参考链接: https://help.aliyun.com/document_detail/27632.html
    '''
    counter = 0
    while counter < TRY_TIME:
        try:
            request = AddBackendServersRequest.AddBackendServersRequest()
            #负载均衡实例的ID
            request.set_LoadBalancerId(params["load_balancer_id"])
            #要添加的后端服务器列表
            request.set_BackendServers(params["backend_servers"])
            response = client.do_action_with_exception(request)

            response_json = json.loads(response)
            return response_json
        except ServerException as e:
            if ExceptionHandler.server_exception(e):
                return e
        except ClientException as e:
            if ExceptionHandler.client_exception(e):
                return e
        finally:
            counter += 1

def create_tcp_listener(params):
    '''
    create_tcp_listener：创建tcp监听
    官网API参考链接: https://help.aliyun.com/document_detail/27594.html
    '''
    counter = 0
    while counter < TRY_TIME:
        try:
            request = CreateLoadBalancerTCPListenerRequest.CreateLoadBalancerTCPListenerRequest()
            #负载均衡实例的ID
            request.set_LoadBalancerId(params["load_balancer_id"])
            #监听的带宽峰值
            request.set_Bandwidth(params["bandwidth"])
            #负载均衡实例前端使用的端口
            request.set_ListenerPort(params["listener_port"])
            #负载均衡实例后端使用的端口
            request.set_BackendServerPort(params["backend_server_port"])
            response = client.do_action_with_exception(request)

            response_json = json.loads(response)
            return response_json
        except ServerException as e:
            if ExceptionHandler.server_exception(e):
                return e
        except ClientException as e:
            if ExceptionHandler.client_exception(e):
                return e
        finally:
            counter += 1


def remove_backend_servers(params):
    '''
    add_backend_servers：删除后端服务器
    官网API参考链接: https://help.aliyun.com/document_detail/27633.html
    '''
    counter = 0
    while counter < TRY_TIME:
        try:
            request = RemoveBackendServersRequest.RemoveBackendServersRequest()
            #负载均衡实例的ID
            request.set_LoadBalancerId(params["load_balancer_id"])
            #要删除的后端服务器列表
            request.set_BackendServers(params["backend_servers"])
            response = client.do_action_with_exception(request)

            response_json = json.loads(response)
            return response_json
        except ServerException as e:
            if ExceptionHandler.server_exception(e):
                return e
        except ClientException as e:
            if ExceptionHandler.client_exception(e):
                return e
        finally:
            counter += 1


def main():
    load_balancer = LoadBalancer(client)
    params = {}
    params["backend_servers"] = [{"ServerId": ECS_INSTANCE_ID, "Weight": "100"}]
    params["bandwidth"] = BANDWIDTH_NOT_LIMITED
    params["listener_port"] = 443
    params["backend_server_port"] = 443

    #创建slb实例
    load_balancer_json = load_balancer.create_load_balancer()
    CommonUtil.log("create_load_balancer", load_balancer_json)

    #slb实例id
    params["load_balancer_id"] = load_balancer_json["LoadBalancerId"]

    #添加后端服务器
    load_balancer_json = add_backend_servers(params)
    CommonUtil.log("add_backend_servers", load_balancer_json)

    #创建tcp监听
    load_balancer_json = create_tcp_listener(params)
    CommonUtil.log("create_tcp_listener", load_balancer_json)

    #删除后端服务器
    load_balancer_json = remove_backend_servers(params)
    CommonUtil.log("remove_backend_servers", load_balancer_json)

    #删除slb实例
    load_balancer_json = load_balancer.delete_load_balancer(params)
    CommonUtil.log("delete_load_balancer", load_balancer_json)


if __name__ == "__main__":
    sys.exit(main())