import socket

host = "110.10.11.153"
port = 10307
buff_size = 128
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (host, port)
sock.connect(server_address)

while True:
    message = input("vsFTP> ").strip()

    if message.lower() == "quit":   # 종료
        break

    list_message = message.split(" ")   # 문자열 공백 단위로 리스트 변환

    if len(list_message) != 2:    # get/put sampleFileName.txt 로 총 2개의 리스트 요소가 생성
        print("잘못된 입력 : 많은 인수 or 적은 인수")
    else:   # 입력이 옳을 경우
        command = list_message[0]
        file_name = list_message[1]

        try:
            sock.send(message.encode())

            if command == "get":
                data = sock.recv(buff_size)
                datastr = ''.join(data.decode())
                if datastr == "False":
                    print("Received from Server : file not found")
                else:
                    textfile = data.decode().splitlines(True)

                    with open(file_name, 'w') as file:  # 파일 입력
                        file.writelines(textfile)

                    print("Server file download Success")
            else:
                data = sock.recv(buff_size)
                print(data.decode())

                if command == "put":
                    with open(file_name, 'r') as file:  # 파일 읽기
                        file_string = file.readlines()

                    file_string = ''.join(file_string) # 파일 읽어서 문자열로 변환

                    # print("Send to Server : {}".format(file_string))  # 보내는 파일 값 print

                    sock.send("{}".format(file_string).encode())  # Server로 파일 내용을 보내는 문장
                    data = sock.recv(buff_size)
                    print(data.decode())

        except Exception as e:
            print("Exception : {}".format(str(e)))

sock.close()