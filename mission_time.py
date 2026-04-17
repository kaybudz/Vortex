# # establishing initial mission time
# hours = '1'
# minutes = '1'
# seconds = '1'
# mission_time = ''
# i = 0

# while i < 100:
#     if int(seconds) < 60:
#         seconds = int(seconds) + 1
#     elif int(seconds) > 60 & int(minutes) < 60:
#         minutes = int(minutes) + 1
#         seconds = 0
#     else:
#         hours = int(hours) + 1
#     mission_time = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
#     i = i + 1
#     print(mission_time)

hours = '2'
minutes = '6'
seconds = '47'
i = 0
while i < 70:
    if int(seconds) < 60:
        seconds = int(seconds) + 1
    elif int(seconds) > 60 & int(minutes) < 60:
        minutes = int(minutes) + 1
        seconds = 0
    else:
        hours = int(hours) + 1
    print(f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
    i = i+1
