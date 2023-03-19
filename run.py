import csv
import datetime
from math import radians, sin, cos, sqrt, atan2
from fit_file import read


fit_datalist = []
controltime_datalist = []

fit_dir = "data/hok_klubmesterskab_2022/CA8D1347.FIT"
control_time_data_dir = "data/hok_klubmesterskab_2022/kontroltider.csv"

total_meters_run = 0






def get_data():
    global fit_datalist
    global control_time_data_tuple
    global controltime_datalist

    fit_datalist = read.read_points(fit_dir)
  

    with open(control_time_data_dir, 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        postkontroller = [{ 'nr':row['nr'], 
            'timestamp': datetime.datetime.fromisoformat(row['timestamp']) } 
          for row in reader]

    controltime_datalist = postkontroller
           
        



# Here we match the times he got to a control post to the time on this fit data
# this can be used to check if he was there and to calculate all post distance, not his running distance
def match_times(number): 
    st_1 = [p for p in fit_datalist if p['timestamp'].astimezone() < controltime_datalist[number]['timestamp']]
    match = controltime_datalist[number]['timestamp'], st_1[-1]
    
    return match

# Haversine formula 
# Calculates the distance between to points (lat, lon)
def distance(point1, point2):
    R = 6371000.0

    lat1, lon1 = radians(point1['latitude']), radians(point1['longitude'])
    lat2, lon2 = radians(point2['latitude']), radians(point2['longitude'])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def get_data_between_posts(start_post, end_post):
    # Find the timestamps for the start and end control points
    start_time = controltime_datalist[start_post]['timestamp']
    end_time = controltime_datalist[end_post]['timestamp']

    # Filter fit_datalist to get the data between the start and end control points
    data_between_posts = [p for p in fit_datalist if start_time <= p['timestamp'].astimezone() <= end_time]

    return data_between_posts



if __name__ == "__main__":

    matched = []
    matched_distance = []
    total_distance = 0

    get_data()



    start_prev = fit_datalist[0]
    # gets matched
    for i in range(len(controltime_datalist)):
        matched.append(match_times(i))

    for i in range(len(matched)):
            inbetween_distance = 0
            points = get_data_between_posts(i -1, i)
            
            for s in points: 
                inbetween_distance += distance(start_prev, s)
                start_prev = s
            
            total_distance += inbetween_distance
       

    current_distance = 0
    start_prev = fit_datalist[0]
    start_prev_time = fit_datalist[0]["timestamp"]
    inbetween_distance = 0
    percentage = 0
    walk_distance = 0
    dist = 0
    run_distance = 0
    # walkling speed in meters
    threshold_speed = 1.5 
    
    #print(matched[1][-1]["timestamp"])
    # gets data in between each matched post
    for i in range(len(matched)):
        
        points = get_data_between_posts(i -1, i)
        current_date = start_prev["timestamp"]

        v = 0
            
        for p in points: 
            inbetween_distance += distance(start_prev, p)
            dist = distance(p, start_prev)
            dt = (p['timestamp'] - start_prev['timestamp']).seconds
            if dt == 0:
                v = 0
            else:
                v = dist / dt
            if v < threshold_speed:
                walk_distance += dist
            else:
                run_distance += dist
            start_prev = p
            

        sub_datetime = current_date - start_prev_time
        
        
        time_delta = datetime.timedelta(seconds=sub_datetime.total_seconds())

        time_taken_str = (datetime.datetime.min + time_delta).strftime('%H:%M:%S')

        
        
        if inbetween_distance == 0:
            percentage = 0
            time_taken_str = "0:00:00"
        else:
            percentage = (inbetween_distance / total_distance) * 100

        matched_distance.append({
            "distance": inbetween_distance,
            "total_distance": total_distance,
            "percentage": percentage,
            "timestamp": time_taken_str,
            "walked": walk_distance,
            "ran": run_distance
        })
    
    post = 1
    for item in matched_distance:
        d = float(item["distance"])
        td = float(item["total_distance"])
        p = float(item["percentage"])
        t = item ["timestamp"]
        w = float(item["walked"])
        r = float(item["ran"])

        print("post: ", post)
        print("{:<10}{:<15}{:<15}{:<20}{:<10}{:<10}".format("distance", "total distance", "remaining %", "Timestamp", "walked", "ran"))
        print("{:<10.2f}{:<15.2f}{:<15.2f}{:<20}{:<10.2f}{:<10.2f} \n".format(d, td, p, t, w, r))
        post += 1
        





