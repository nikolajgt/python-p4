import gpxpy
import os

# ---------------->8
#skraldet fra https://www.programcreek.com/python/example/122591/gpxpy.parse Example 2

def read_gpx_file(filename):
    try:
        with open(filename, "r") as f:
            points_list = []
            prev_point = None
            head, tail = os.path.split(filename)
            code_route = tail.replace(".gpx", "")
            try:
                gpx = gpxpy.parse(f)
                for point in gpx.walk(only_points=True):
                    speed = point.speed_between(prev_point)
                    if speed is None:
                        speed = 0

                    time_difference = point.time_difference(prev_point)
                    if time_difference is None:
                        time_difference = 0

                    distance = point.distance_3d(prev_point)
                    if not distance:
                        distance = point.distance_2d(prev_point)
                    if distance is None:
                        distance = 0

                    points_list.append([code_route, point.latitude, point.longitude, point.elevation,
                                                point.time, speed, time_difference, distance, gpx.name])

                    prev_point = point
            except Exception as e:
                raise TrackException('GPX file "' + filename + '" malformed', e)
    except FileNotFoundError as e:
        raise TrackException('GPX file "' + filename + '" not found', e) 

    return points_list
# 8<-------

# 8<----  https://github.com/acsicuib/YAFS/blob/master/src/trackanimation/utils.py
class TrackException(Exception):
    """
    Generic exception for TrackAnimation
    """

    def __init__(self, msg, original_exception):
        super(TrackException, self).__init__(msg + (": %s" % original_exception))
        self.original_exception = original_exception
# ----->8

def main():

    filename = r"projektopgave\data\activity_7403521010.gpx"
    points = read_gpx_file(filename)


    print(len(points))
    print(points[0])
    print(points[1])
    
    print(points[100])

    #print(points)

if __name__ == '__main__':
    main()