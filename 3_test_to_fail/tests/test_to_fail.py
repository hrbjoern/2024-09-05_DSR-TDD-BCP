# CERTIFICATION REQUIREMENTS

# The wireless radio meter is sending a Mobile telegram every minute (with timing accuracy tolerance 10%) with the
# volume of water that it measured that passed through it. The water is pumped under pressure only one way through the
# meter at a rate of exactly 10 dm^3 per minute, assume no problems with the pump delivering the water from the tap.
# The volume is measured from zero every time You start recording telegrams.
# Every hour a Static telegram is sent with the meter status which shall be stating OK throughout the whole meter
# operation.

# TODO Write tests that record telegrams and are checking if the meter is up the certification requirements
# TODO Report all inconsistencies with the required parameters

import pytest
from datetime import datetime, timedelta
from collections import defaultdict
from pprint import pp


# DO NOT LOOK INTO THE RECORD_TELEGRAMS FUNCTION AS IT WILL SPOIL THE MYSTERY!
from water_meter import record_telegrams

if __name__ == "__main__":
    telegrams = record_telegrams(duration_minutes=6)
    for telegram in telegrams:
            print(telegram)

# Check for telegram status: 
@pytest.mark.parametrize("duration_minutes", [1800])
def test_static_telegrams_status(duration_minutes):
    telegrams = record_telegrams(duration_minutes)
    errorgrams = []
    static_times = defaultdict()

    # Check if all static telegrams have status "OK"
    for telegram in telegrams:
        if "Static telegram" in telegram:
            if not "STATUS: OK" in telegram: 
                #print(telegram)
                errorgrams.append(telegram)
            #assert "STATUS: OK" in telegram

    pp(errorgrams)
    
# Check for static telegram timing:     
@pytest.mark.parametrize("duration_minutes", [1800])
def test_static_telegrams_timing(duration_minutes):
    telegrams = record_telegrams(duration_minutes)
    static_times = []
    errortimes = {}

    for telegram in telegrams:
        if "Static telegram" in telegram:
            timestamp_str = telegram.split(" at ")[1].split(" STATUS:")[0]
            static_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            static_times.append(static_time)

    # Check if STATIC telegrams appear once per hour: 
    for i in range(1, len(static_times)):
        time_difference = static_times[i] - static_times[i-1]
        maximum_difference = timedelta(minutes=61.)
        minimum_difference = timedelta(minutes=59.)
        # assert minimum_difference <= time_difference <= maximum_difference, \
        #         f"Wrong static time difference at {static_times[i]}"   
        if not minimum_difference <= time_difference <= maximum_difference:
            #print(static_times[i].time(), ime_difference)
            #print(static_times[i].time(), time_difference)
            errortimes[str(static_times[i].time())] = str(time_difference)

    print(errortimes)


# Check for mobile telegram timing: 
@pytest.mark.parametrize("duration_minutes", [600])  # Test for 600 minutes
def test_mobile_telegrams_timing(duration_minutes):
    telegrams = record_telegrams(duration_minutes)
    mobile_times = []

    # Extract timestamps of mobile telegrams
    for telegram in telegrams:
        if "Mobile telegram" in telegram:
            timestamp_str = telegram.split(" at ")[1].split(" Volume:")[0]
            mobile_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            mobile_times.append(mobile_time)

    # Check distance between mobile telegrams
    for i in range(1, len(mobile_times)):
        time_difference = mobile_times[i] - mobile_times[i-1]
        maximum_difference = timedelta(minutes=1.1)
        minimum_difference = timedelta(minutes=0.9)
        
        assert minimum_difference <= time_difference <= maximum_difference, \
                f"Wrong mobile time difference at {mobile_times[i]}" 


@pytest.mark.parametrize("duration_minutes, volume_increase_per_min", [(600, 10.)])  # Test for 600 minutes
def test_volume_accu(duration_minutes, volume_increase_per_min):
    telegrams = record_telegrams(duration_minutes)
    volume = 0

    # Check if volume increases by volume_increase_per_min at every mobile telegram
    for telegram in telegrams:
        if "Mobile telegram" in telegram:
            volume_str = telegram.split("Volume: ")[1]
            current_volume = float(volume_str)
            if telegrams.index(telegram) == 0: 
                assert (current_volume == 0  or 
                        current_volume == round(0 + volume_increase_per_min, 1) ), \
                        "Volume error in "+telegram
            assert current_volume == round(volume + volume_increase_per_min, 1), \
                    "Volume error in "+telegram
            volume = current_volume


if __name__ == "__main__":
    pytest.main()


