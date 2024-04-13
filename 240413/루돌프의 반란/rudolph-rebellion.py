from collections import deque

N, M, P, C, D = map(int, input().split())

# 자료구조
# 1) 게임판 위의 산타, 루돌프 표시 (N + 1 * N + 1 크기 격자)
table = [[-1] * (N + 1) for _ in range(N + 1)]

# 2) 산타의 점수 기록
scores = [0] * (P + 1)

# 3) 루돌프 위치
r_loc = None

# 4) 산타 번호, 위치
santas = {}

# 5) 산타 상태
santas_status = [0] * (P + 1)

# 6) 탈락하지 않은 산타 수
num_santa = P

# 입력 받기 
r_loc = list(map(int, input().split()))

for _ in range(P):
    tmp = list(map(int, input().split()))
    santas[str(tmp[0])] = tmp[1:]


def dist(x1, y1, x2, y2):
    return (x1-x2)*(x1-x2) + (y1-y2)*(y1-y2)

# M턴 반복
for turn in range(M):
    # 만약 모든 산타가 게임 탈락한 경우, 그 즉시 게임 종료. 
    if num_santa <= 0:
        break
        
    # [1] 루돌프 이동
    # [1-1] 가장 가까운 산타 찾기(거리 - 큰 r좌표 - 큰 c좌표) 
    # 기절 상태여도 ok. 
    # TODO: sort함수로 구현
    sorted_santas = sorted(santas.items(), key = lambda x: (dist(r_loc[0], r_loc[1], x[1][0], x[1][1]), -x[1][0], -x[1][1]))
 
    # [1-2] 8방향 중 가장 가까워지는 한 방향 선택하기
    # TODO: 산타와 루돌프 좌표 차이를 이용해, dr, dc 구하기
    target_s_idx, target_s_x, target_s_y = int(sorted_santas[0][0]), sorted_santas[0][1][0], sorted_santas[0][1][1]
    r_x, r_y = r_loc[0], r_loc[1]

    dr, dc = 0, 0
    if target_s_x > r_x:
        dr = 1
    elif target_s_x < r_x:
        dr = -1

    if target_s_y > r_y:
        dc = 1
    elif target_s_y < r_y:
        dc = -1
         
    # [1-3] 루돌프 이동하기
    r_loc = [r_x + dr, r_y + dc]
    
    # [1-4] 충돌이 일어난 경우, 산타는 C 점을 얻고, 루돌프가 이동한 방향으로 C칸 밀려남.  그리고 기절. 
    # 밀려난 위치가 게임판 밖이라면 게임 탈락
    if target_s_x == r_x + dr and target_s_y == r_y + dc:
        scores[target_s_idx] += C
        s_dr, s_dc = dr * C, dc * C

        # 밀려난 위치가 게임판 밖이라면?
        if target_s_x + s_dr <= 0 or target_s_x + s_dr > N or target_s_y + s_dc <= 0 or target_s_y + s_dc > N:
            santas.pop(str(target_s_idx))
            santas_status[target_s_idx] = -1
            num_santa -= 1

        # 밀려난 위치가 게임판 안이라면
        else:
            # 밀려난 칸에 다른 산타가 있는 경우 상호작용 발생
            already_santa = [k for k, v in santas.items() if v == [target_s_x + s_dr , target_s_y + s_dc]]
            if len(already_santa) != 0:
                queue = deque()
                queue.append(already_santa[0])
                santas[str(target_s_idx)] = [target_s_x + s_dr , target_s_y + s_dc]
                santas_status[target_s_idx] = 2

                while queue:
                    s_idx = queue.popleft()
                    s_r, s_c = santas[str(s_idx)]

                    # 밀려난 위치가 게임판 밖이라면?
                    if s_r + dr <= 0 or s_r + dr > N or s_c + dc <= 0 or s_c + dc > N:
                        santas.pop(str(s_idx))
                        santas_status[int(s_idx)] = -1
                        num_santa -= 1

                    # 밀려난 위치가 게임판 안이라면
                    else:       
                        already_santa = [k for k, v in santas.items() if v == [s_r + dr , s_c + dc]]
                        # 그 자리에 다른 산타가 있다면 queue에 넣기
                        if len(already_santa) != 0:
                            queue.append(int(already_santa[0]))

                        santas[s_idx] = [s_r + dr , s_c + dc]
            # 밀려난 칸에 다른 산타가 없다면,
            else:
                santas[str(target_s_idx)] = [target_s_x + s_dr , target_s_y + s_dc]
                santas_status[target_s_idx] = 2

    # [2] 산타가 순서대로 이동
    # 1번부터 P번까지 순서대로 이동
    for s_idx in range(1, P+1):
        # 기절하거나 탈락한 산타는 SKIP
        if santas_status[s_idx] != 0:
            continue

        s_r, s_c = santas[str(s_idx)]
        r_r, r_c = r_loc[0], r_loc[1]

        # [2-1] 루돌프와 가까워지는 4방향 중 하나로 1칸 찾기. (여러 개라면, 상우하좌 순 / 없다면 움직이지 않음. 다른 산타가 있는 칸으로나 게임판 밖으로는 움직일 수 없음.)
        d = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        s_dr, s_dc = 0, 0
        cur_dist = dist(r_r, r_c, s_r, s_c)
        available_step = []
        for dr, dc in d:
            already_santa = [k for k, v in santas.items() if v == [s_r + dr , s_c + dc]]
            # 다른 산타가 있는 칸으로 움직일 수 없음.
            if len(already_santa) != 0:
                continue
            # 게임판 밖으로는 움직일 수 없음.
            if s_r + dr <= 0 or s_r + dr > N or s_c + dc <= 0 or s_c + dc > N:
                continue
            available_step.append([dist(r_r, r_c, s_r + dr, s_c + dc), dr, dc])
        
        if len(available_step) != 0:
            available_step.sort(key = lambda x : (x[0]))
            if cur_dist > available_step[0][0]:
                s_dr, s_dc = available_step[0][1], available_step[0][2]
        # print(s_dr, s_dc)
        
        
        # 산타 이동
        s_new_r, s_new_c = s_r + s_dr, s_c + s_dc
        santas[str(s_idx)] = [s_new_r, s_new_c]

        # [2-2] 움직인 칸에 루돌프가 있어 충돌이 일어난 경우, 산타는 D점을 얻고, 자신이 이동해온 반대 방향으로 D칸 밀려남. 그리고 기절. 
        # 밀려난 위치가 게임판 밖이라면 게임 탈락
        # 밀려난 칸에 다른 산타가 있는 경우 상호작용 발생
        
        if s_new_r == r_r and s_new_c == r_c:
            scores[s_idx] += D
            
            s_new_dr, s_new_dc = s_dr * -D, s_dc * -D

            # 밀려난 위치가 게임판 밖이라면?
            if s_new_r + s_new_dr <= 0 or s_new_r + s_new_dr > N or s_new_c + s_new_dc <= 0 or s_new_c + s_new_dc > N:
                santas.pop(str(s_idx))
                santas_status[s_idx] = -1
                num_santa -= 1

            # 밀려난 위치가 게임판 안이라면
            else:
                # [2-3] 상호작용
                # 충돌로 이동했을 때, 그 칸에 산타가 있다면 그 산타는 1칸 해당 방향으로 밀려남. 연쇄적으로. 
                # TODO: queue를 이용해서 구현..? 
                already_santa = [k for k, v in santas.items() if v == [s_new_r + s_new_dr , s_new_c + s_new_dc]]
                if len(already_santa) != 0:
                    queue = deque()
                    queue.append(already_santa[0])
                    santas[str(s_idx)] = [s_new_r + s_new_dr , s_new_c + s_new_dc]
                    santas_status[s_idx] = 2

                    dr, dc = s_new_dr / D, s_new_dc / D
                    while queue:
                        s_idx = queue.popleft()
                        s_r, s_c = santas[s_idx]

                        # 밀려난 위치가 게임판 밖이라면?
                        if s_r + dr <= 0 or s_r + dr > N or s_c + dc <= 0 or s_c + dc > N:
                            santas.pop(s_idx)
                            santas_status[int(s_idx)] = -1
                            num_santa -= 1

                        # 밀려난 위치가 게임판 안이라면
                        else:       
                            already_santa = [k for k, v in santas.items() if v == [s_r + dr , s_c + dc]]
                            # 그 자리에 다른 산타가 있다면 queue에 넣기
                            if len(already_santa) != 0:
                                queue.append(int(already_santa[0]))

                            santas[s_idx] = [s_r + dr , s_c + dc]
                # 밀려난 칸에 산타가 없다면
                # 밀려난 칸에 다른 산타가 없다면,
                else:
                    santas[str(s_idx)] = [s_new_r + s_new_dr , s_new_c + s_new_dc]
                    santas_status[s_idx] = 2

    # # [3] 턴 종료 
    # # [3-1] 매 턴 아직 탈락하지 않은 산타들에게 1점씩 추가 부여. 
    # print(turn + 1, "턴 종료")
    for s_idx in range(1, P + 1):
        if santas_status[s_idx] == -1:
            continue
        elif santas_status[s_idx] != 0:
            # [3-2] 기절 상태 산타들 상태값 -1
            santas_status[s_idx] -= 1
        scores[s_idx] += 1
    # print("루돌프: ", r_loc)
    # print("산타: ",santas)
    # print("점수:", scores)
    # print()
# [4] 턴 종료
for idx in range(1, P+1):
    print(scores[idx], end=" ")