import vtk
import sys, os
import numpy as np

import math

"""

"""

def dst(p1,p2):
    return math.sqrt( (p1[0]-p2[0])**2 +
                      (p1[1]-p2[1])**2 +
                      (p1[2]-p2[2])**2)

def load_polydata(filename):
    reader = vtk.vtkPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader.GetOutput()

xy_res, z_res = float(sys.argv[2]), float(sys.argv[3])

raw_pipeline = load_polydata(sys.argv[4])
hq_pipeline = load_polydata(sys.argv[5])
lq_pipeline = load_polydata(sys.argv[6])

hq_locator = vtk.vtkPointLocator()
hq_locator.SetDataSet(hq_pipeline)
hq_locator.BuildLocator()

lq_locator = vtk.vtkPointLocator()
lq_locator.SetDataSet(lq_pipeline)
lq_locator.BuildLocator()

hq_points_results = []
lq_points_results = []

for i in range(raw_pipeline.GetPoints().GetNumberOfPoints()):
    raw_point = raw_pipeline.GetPoints().GetPoint(i)

    hq_point_idx = hq_locator.FindClosestPoint(raw_pipeline.GetPoints().GetPoint(i))
    hq_point = hq_pipeline.GetPoints().GetPoint(hq_point_idx)

    lq_point_idx = lq_locator.FindClosestPoint(raw_pipeline.GetPoints().GetPoint(i))
    lq_point = lq_pipeline.GetPoints().GetPoint(lq_point_idx)

    hq_dist = dst(raw_point, hq_point)
    lq_dist = dst(raw_point, lq_point)

    hq_points_results.append(hq_dist)
    lq_points_results.append(lq_dist)

hq_mean = np.array(hq_points_results)
lq_mean = np.array(lq_points_results)

raw_point_no = raw_pipeline.GetPoints().GetNumberOfPoints()
hq_point_no = hq_pipeline.GetPoints().GetNumberOfPoints()
lq_point_no = lq_pipeline.GetPoints().GetNumberOfPoints()

print "%s\t%f\t%f\t%d\t%d\t%d\t0\t%f\t%f" % \
        (os.path.basename(sys.argv[1]), \
         xy_res, z_res,
         raw_point_no, hq_point_no, lq_point_no, \
         np.mean(hq_mean), np.mean(lq_mean))
