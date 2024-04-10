from queue import PriorityQueue
from collections import deque

# 1. 채점기 준비
# N개의 채점기 준비.
# 초기 문제 url에 해당하는 u0이 주어짐
# url: 도메인/문제id (문제id는 1~10억 이하의 정수값)
# N개의 채점기는 1~N번의 번호가 붙어있음
# 0초에 채점 우선순위가 1이면서 url이 u0인 초기 문제에 대한 채점 요청이 들어오게 됨.

def ready(order):
    N = int(order[0])
    u0 = order[1]
    domain, pid = u0.split("/")
    pid = int(pid)

    # 채점기 상태 설정 
    global markers
    markers = [0] * N
    
    # 현재 채점 중인 url 기록하는 자료구조 설정
    global marking_url
    marking_url = [None] * N

    # 대기큐에 입력 (우선순위, 초, 도메인, 문제번호)
    wait_queue.put((1, 0, domain, pid))

    # 채점 대기 큐에 들어있는 url  따로 기록하는 자료구조
    url_in_wait_queue.append(u0)

    # 도메인별 최근 채점 기록
    domain_info[domain] = [None, None]

# 2. 채점 요청
# t초에 채점 우선순위가 p이면서 url이 u인 문제에 대한 채점 요청이 들어오게 됨.
# 채점 대기 큐에 있는 task 중 정확히 u와 일치하는 url이 단 하나라도 존재하면 큐에 추가하지 않고 넘어감

def request(order):
    t = int(order[0])
    p = int(order[1])
    domain, pid = order[2].split("/")

    # [1-1] 채점 대기 큐에 같은 url이 있다면 넘어감
    if order[2] in url_in_wait_queue:
        # print("이미 있습니다.")
        return
    
    # [1-2] 아니라면,
    # 대기큐에 입력 (우선순위, 초, 도메인, 문제번호)
    wait_queue.put((p, t, domain, pid))
    
    # 채점 대기 큐에 들어있는 url  따로 기록하는 자료구조
    url_in_wait_queue.append(order[2])

    # 도메인별 최근 채점 기록
    if domain not in domain_info:
        domain_info[domain] = [None, None]


# 3. 채점 시도
# t초에 채점 대기 큐에서 즉시 채점이 불가능한 경우를 제외하고,
# 남은 task 중 우선순위가 가장 높은 채점 task를 골라 채점 진행

# 채점이 될 수 없는 조건
    # 해당 task의 도메인이 현재 채점 진행중인 도메인 중 하나라면 불가
    # 해당 task의 도메인과 정확히 일치하는 도메인에 대해 가장 최근에 진행된 채점 시작시간이 start, 종료시간 start+gap였고,
    # 현재 시간 t가 start + 3 *gap보다 작다면, 채점 불가

# 우선순위
    # 채점 우선순위 p의 번호가 작을 수록 우선순위가 높다
    # 채점 우선순위가 동일하다면 채점 task가 채점 대기 큐에 들어온 시간이 더 빠를수록 우선순위가 높다

# t초에 채점 가능한 task가 단 하나라도 있었다면, 쉬고 있는 채점기 중 가장 번호가 작은 채점기가 우선순위가 가장 높은 채점 task에 대해 채점 시작
# 쉬고 있는 채점기가 없다면 요청을 무시하고 넘어감

def mark(order):
    current_t = int(order[0])

    # 쉬고 있는 채점기가 없다면 요청을 무시하고 넘어감.
    if 0 not in markers:
        return
    
    # 채점 불가능한 문제들 넣어두는 queue
    skip_problems = deque()

    while wait_queue.qsize():
        # [1] 우선순위가 가장 높은 task 뽑기
        p, t, domain, pid = wait_queue.get()

        # [2-1] 채점이 불가능하다면 queue에 넣어두고 다시 [1-1]로 넘어가기
        # [2-1-1] 해당 task의 도메인이 현재 채점 진행중인 도메인 중 하나라면 불가
        if domain + "/" + str(pid) in marking_url:
            skip_problems.append((p, t, domain, pid))
            continue

        # [2-1-2] 해당 task의 도메인과 정확히 일치하는 도메인에 대해 가장 최근에 진행된 채점 시작시간이 start, 종료시간 start+gap였고, 현재 시간 t가 start + 3 *gap보다 작다면, 채점 불가
        if domain in domain_info:
            if domain_info[domain][0] != None and domain_info[domain][1] != None:
                start, end = domain_info[domain]
                gap = end - start
                
                # print("current_t: ", current_t, "start + 3 * gap: ", start + 3 * gap)
                if current_t < start + 3 * gap:
                    skip_problems.append((p, t, domain, pid))
                    continue
        
        # [2-2] 채점이 가능하다면 쉬고 있는 채점기 중 가장 번호가 작은 채점기에 할당.
        available_marker_idx = markers.index(0)

        # 채점기 상태 기록하는 자료구조
        markers[available_marker_idx] = 1

        # 현재 채점 중인 url 기록하는 자료구조
        marking_url[available_marker_idx] = (domain+"/"+str(pid))

        # 도메인 별 최근 채점 기록 기록하는 자료구조 (key: 도메인이름, value: [채점시작시간, 종료시간])
        domain_info[domain] = [current_t, None]

        # 채점 대기 큐에 들어있는 url  따로 기록하는 자료구조
        url_in_wait_queue.remove(domain+"/"+str(pid))

        break

    # 채점 불가능한 문제들 다시 wait queue에 넣기
    while skip_problems:
        wait_queue.put(skip_problems.pop())

# 4. 채점 종료
# t초에 J(id)번 채점기가 진행하던 채점이 종료됨. J(id) 채점기는 다시 쉬는 상태가 된다.
# 만약 진행하던 채점이 없었다면 이 명령은 무시

def terminate(order):
    t = int(order[0])
    to_terminate_marker_idx = int(order[1]) - 1
    
    # [1-1] 만약 진행하던 채점이 없었다면 이 명령은 무시
    if marking_url[to_terminate_marker_idx] == None:
        return

    # [1-2] 아니라면, 채점 종료
    # 현재 채점 중이던 도메인
    url = marking_url[to_terminate_marker_idx]
    domain = url.split("/")[0]

    # 채점기 상태 기록하는 자료구조
    markers[to_terminate_marker_idx] = 0

    # 현재 채점 중인 url 기록하는 자료구조
    marking_url[to_terminate_marker_idx] = None

    # 도메인 별 최근 채점 기록 기록하는 자료구조 (key: 도메인이름, value: [채점시작시간, 종료시간])
    domain_info[domain][1] = t

    # # 채점 대기 큐에 들어있는 url  따로 기록하는 자료구조
    # url_in_wait_queue.remove(url)

# 5. 채점 대기 큐 조회
# 시간 t에 채점 대기 큐에 있는 채점 task의 수를 출력
def inquiry(order):
    t = int(order[0])
    
    # print("----------------")
    print(wait_queue.qsize())
    # print(len(url_in_wait_queue))

########################################
if __name__ == "__main__":
    Q = int(input())

    # 채점기 상태 기록하는 자료구조
    markers = None

    # 현재 채점 중인 url 기록하는 자료구조
    marking_url = []

    # 도메인 별 최근 채점 기록 기록하는 자료구조 (key: 도메인이름, value: [채점시작시간, 종료시간])
    domain_info = {}

    # 채점 대기 큐(우선순위 큐)
    wait_queue = PriorityQueue()

    # 채점 대기 큐에 들어있는 url  따로 기록하는 자료구조
    url_in_wait_queue = set()

    # Q번 읽기
    for idx in range(Q):
        order = input().split()
        # print(order)
        order_num = order[0]

        if order_num == '100':
            ready(order[1:])
        elif order_num == '200':
            request(order[1:])
        elif order_num == '300':
            mark(order[1:])
        elif order_num == '400':
            terminate(order[1:])
        elif order_num == '500':
            inquiry(order[1:])