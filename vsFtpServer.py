import os
import sys
import errno
import signal
import socket

BACKLOG = 5  # 큐 대기열
host = ""  # 자동 아이피 할당,  "203.250.133.88"
port = 10307


def collect_zombie(signum, frame):
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)  # 아무 좀비 프로레스 처리, 없으면 빠져나오기
            if pid == 0:  # 좀비 프로세스가 없다면 0이 나옴
                break
        except:
            # waitpid 하려고 보니 돌고 있는 자녀 프로세스가 없는 경우의 에러 처리
            break


def do_echo(sock):
    while True:
        message = sock.recv(1024)
        if message:  # message 가 0이 나오기 전까지, (TCP)상대가 연결을 종료하면 0이 나옴, 연결은 있으나 message가 없으면 recv에서 blocking 됨
            global count, put_state, file_name
            count += 1

            recv_message_list = message.decode().strip().split(" ")  # recv_message_list

            if recv_message_list[0] == "put":  # 첫 리스트 값이 put 으로 들어온 경우, 파일 값을 입력 받는다
                '''
                1. 받은 내용 클라이언트에게 보내기
                2. 파일 내용 받기
                3. 완료 메시지 보내기
                '''

                # 1

                file_name = recv_message_list[1]  # 파일 이름 받기
                put_state = True  # 파일 입력을 받을 상태로 True

                # print("recv message : {}".format(message.decode()))  # 받은 message 값 print
                # recvstr = "{} | {} : received message is ".format(count, put_state) + message.decode()
                # print("send Message : " + recvstr + "\n")

                sock.sendall("Server received message : ".encode() + message)  # 받은 메시지 클라이언트로 보내기

            if recv_message_list[0] != "put" and put_state:  # put 입력이 아니고 put_state 가 True 인 파일 받아드리기 단계

                textfile = message.decode().splitlines(True)    # 문자열 리스트로 변환, True 는 줄바꿈 포함

                with open(file_name, 'w') as file:  # 파일 입력
                    file.writelines(textfile)

                file_name = ""  # 파일 이름 삭제
                put_state = False  # 파일 입력을 받지 않을 상태로 False

                # print("recv message : {}".format(message.decode()))  # 받은 message 값 print
                # recvstr = "{} | {} : received message is ".format(count, put_state) + ''.join(recv_message_list)  # 파일 입력 값 클라이언트로 전송
                # print("susc send Message : " + recvstr + "\n")

                sock.sendall("file upload completed".encode())  # 받은 메시지 클라이언트로 보내기

            if recv_message_list[0] == "get":  # 첫 리스트 값이 put 으로 들어온 경우, 파일 값을 입력 받는다
                '''
                1. 파일 내용 클라이언트에게 보내기 / 없으면 “file not found" 보내기
                '''

                # 1

                file_name = recv_message_list[1]  # 파일 이름 받기

                try:
                    with open(file_name, 'r') as file:  # 파일 읽기
                        file_string = file.readlines()

                    file_string = ''.join(file_string) # 파일 읽어서 문자열로 변환
                    sock.send("{}".format(file_string).encode())  # 클라이언트로 파일 내용을 보내는 문장

                except FileNotFoundError:
                    sock.send("False".encode())  # 파일 없을 때 전송문

                file_name = ""  # 파일 이름 삭제


global count, put_state, file_name
put_state = False

signal.signal(signal.SIGCHLD, collect_zombie)

conn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP 소켓

conn_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # port 재사용 가능하게
conn_sock.bind((host, port))  # 서버 자신 할당
conn_sock.listen(BACKLOG)  # passive open(대기열)

print("Listening on port {}".format(port))

count = 0

while True:
    try:
        data_sock, client_address = conn_sock.accept()  # conn_sock 은 대표전화 연결용, 직접 연결은 data_sock으로 연결
    except IOError as e:
        code, msg = e.args
        if code == errno.EINTR:
            continue
        else:
            raise  # 다른 오류가 들어오면 예외를 처리하는 부분

    pid = os.fork()  # 서비스 시작, 부모 자녀 두 개가 생성됨
    if pid == 0:  # 자녀 프로세스
        conn_sock.close()  # 클라이언트의 부모 소켓 해지
        do_echo(data_sock)  # echo 서비스
        os._exit(0)  # 좀비 상태 -> 부모가 SigHandler 종료 -> 종료

    data_sock.close()  # 부모에서 자기가 사용하지 않는 소켓 해지
