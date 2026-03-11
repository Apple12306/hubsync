#!/usr/bin/env python3
# python 脚本
# 根据传入的参数，使用dockerhub 搜索所有镜像，并将结果保存到result.json文件中
import argparse
import requests
import json
import time

def login_dockerhub(username, password):
    """
    登录Docker Hub并获取访问令牌
    :param username: Docker Hub用户名
    :param password: Docker Hub密码或访问令牌
    :return: 访问令牌
    """
    url = "https://hub.docker.com/v2/users/login/"
    payload = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        token = response.json().get('token')
        print("Docker Hub登录成功")
        return token
    except Exception as e:
        print(f"Docker Hub登录失败: {e}")
        return None

def search_dockerhub_images(query, page_size=100, token=None):
    """
    搜索Docker Hub镜像
    :param query: 搜索关键词
    :param page_size: 每页返回的结果数
    :param token: Docker Hub访问令牌
    :return: 所有搜索结果
    """
    results = []
    page = 1
    has_more = True
    
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    while has_more:
        url = f"https://registry.hub.docker.com/v2/search/repositories/?query={query}&page={page}&page_size={page_size}"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # 添加当前页的结果
            results.extend(data.get('results', []))
            
            # 检查是否有更多结果
            has_more = data.get('next') is not None
            page += 1
            
            # 避免请求过快被限制
            time.sleep(1)
        except Exception as e:
            print(f"搜索过程中出错: {e}")
            has_more = False
    
    return results

def main():
    parser = argparse.ArgumentParser(description='搜索Docker Hub镜像并保存结果')
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('--output', default='result.json', help='输出文件路径')
    parser.add_argument('--page-size', type=int, default=100, help='每页结果数')
    parser.add_argument('--username', help='Docker Hub用户名')
    parser.add_argument('--password', help='Docker Hub密码或访问令牌')
    
    args = parser.parse_args()
    
    # 登录Docker Hub获取令牌
    token = None
    if args.username and args.password:
        token = login_dockerhub(args.username, args.password)
    
    print(f"开始搜索Docker Hub镜像，关键词: {args.query}")
    results = search_dockerhub_images(args.query, args.page_size, token)
    
    print(f"搜索完成，找到 {len(results)} 个镜像")
    
    # 保存结果到文件
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存到 {args.output}")

if __name__ == "__main__":
    main()
