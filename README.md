# I am alive

컴퓨터야 나 안잔다


## 개발환경
python 3.9


## 구동 및 확인요소

python alive_mouse.py로 동작

argument  
--animation {$ANIMATION_NAME} | 동작중 애니메이션 ['spinner', 'clock', 'ellipsis', 'pulsing', 'bounce', 'arrow'] 중 택 1  
--interval {$INTERVAL} | 마우스 동작 간격(초) int값 입력, 최소 1초

config
break_start | 쉬는 시간 시작시간, 쉬는 시간에는 마우스가 동작하지 않음
break_end | 쉬는 시간 종료시간, 쉬는 시간에는 마우스가 동작하지 않음
work_end | 강제 종료 시간, 단, 안전하게 프로그램을 종료하려면 enter키를 눌러 timer_thread를 종료해야함