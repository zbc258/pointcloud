import cupy as np
import open3d as o3d
import matplotlib.pyplot as plt
from tool import *
def pass_through( pcd, limit_min, limit_max, filter_value_name):
	"""
	直通滤波
	:param cloud:输入点云
	:param limit_min: 滤波条件的最小值
	:param limit_max: 滤波条件的最大值
	:param filter_value_name: 滤波字段(x or y or z)
	:return: 位于[limit_min,limit_max]范围的点云
	
"""
	points=pcd_to_point(pcd)
	if filter_value_name == "x":

		ind = np.where((points[:, 0] >= limit_min) & (points[:, 0] <= limit_max))[0]
		x_cloud =   pcd.select_by_index(ind)
		return x_cloud

	elif filter_value_name == "y":

		ind = np.where((points[:, 1] >= limit_min) & (points[:, 1] <= limit_max))[0]
		y_cloud =  pcd.select_by_index(ind)
		return y_cloud

	elif filter_value_name == "z":

		ind = np.where((points[:, 2] >= limit_min) & (points[:, 2] <= limit_max))[0]
		z_cloud =   pcd.select_by_index(ind)
		return z_cloud
def fps_filter(point_cloud):
	filtered_points = []
	# 随机选取第一个点当做FPS下采样的起点
	point_first_index = np.random.randint(0, len(point_cloud))
	filtered_points.append(point_cloud[point_first_index])
	# 按照50%作为下采样的目标点数
	downsample_point_num = len(point_cloud) * 0.5
	for i in range(int(downsample_point_num)):
		ipoint_jpoint_distance = []
		if(i == 0):     # 使用随机选取的点作为FPS的第一个点
			i_x = point_cloud[point_first_index][0]
			i_y = point_cloud[point_first_index][1]
			i_z = point_cloud[point_first_index][2]
			for j in range(len(point_cloud)):
				j_x = point_cloud[j][0]
				j_y = point_cloud[j][1]
				j_z = point_cloud[j][2]
				distance = pow((i_x-j_x), 2) + pow((i_y-j_y), 2) + pow((i_z-j_z), 2)
				ipoint_jpoint_distance.append(distance)
			distance_sort = np.argsort(ipoint_jpoint_distance)
			filtered_points.append(point_cloud[distance_sort[-1]])
			continue
		# 遍历点云中的每一个点
		for j in range(len(point_cloud)):
			j_x = point_cloud[j][0]
			j_y = point_cloud[j][1]
			j_z = point_cloud[j][2]
			distance_list = []
			# 计算遍历到的原点云中的点与已采到的点之间的距离
			for k in range(len(filtered_points)):
				point_repeat = True     # point_repeat防止比较同一个点之间的距离
				k_x = filtered_points[k][0]
				k_y = filtered_points[k][1]
				k_z = filtered_points[k][2]
				if (j_x == k_x and j_y == k_y and j_z == k_z):
					point_repeat = False
					break
				distance = pow((i_x-j_x), 2) + pow((i_y-j_y), 2) + pow((i_z-j_z), 2)
				distance_list.append(distance)
			if point_repeat is True:
				distance_avg = np.mean(distance_list)
				ipoint_jpoint_distance.append(distance_avg)
		distance_sort = np.argsort(ipoint_jpoint_distance)          # 对距离排序，返回索引序号
		filtered_points.append(point_cloud[distance_sort[-1]])      # 将具有最大距离对应的点加入filtered_points
	print(len(filtered_points))
	# 把点云格式改成array，并对外返回
	filtered_points = np.asarray(filtered_points, dtype=np.float64)
	return filtered_points
def median_filter(pcd, radius):
	kdtree = o3d.geometry.KDTreeFlann(pcd)
	points_copy = np.asarray(pcd.points)
	points = np.asarray(pcd.points)
	num_points = len(pcd.points)

	for i in range(num_points):
		k, idx, _ = kdtree.search_radius_vector_3d(pcd.points[i], radius)
		if k < 3:
			continue

		neighbors = points[idx, :]
		median = np.median(neighbors, 0)

		points_copy[i] = median

	pcd.points = o3d.utility.Vector3dVector(points_copy)
def hull_pcd(pcd,ax):

   
	hull, idx = pcd.compute_convex_hull()
	hull_cloud = pcd.select_by_index(idx)#计算凸包的顶点
	hull_ls = o3d.geometry.LineSet.create_from_triangle_mesh(hull)#将顶点连接成凸包
	n=np.asarray(hull_ls.points)#导出凸包顶点坐标
	l=np.asarray(hull_ls.lines)#导出凸包连线的点集索引（open3d中连线以两点的序号表示）
	wid=l.shape[0]
	S=np.asarray(n[(l[:,0])])
	T=np.asarray(n[(l[:,1])])
	for i in range(0,wid):
		x1=S[i,0]
		y1=S[i,1]
		z1=S[i,2]
		x2=T[i,0]
		y2=T[i,1]
		z2=T[i,2]
		ax.plot([x1,x2],[y1,y2],[z1,z2],c='b', marker=".")
def create_obb(pcd,ax):
	
	obb=pcd.get_oriented_bounding_box()
	vertex=np.asarray(obb.get_box_points())
	ax.plot([vertex[0,0],vertex[2,0],vertex[7,0],vertex[1,0],vertex[0,0],vertex[3,0],vertex[6,0],vertex[1,0]],
			[vertex[0,1],vertex[2,1],vertex[7,1],vertex[1,1],vertex[0,1],vertex[3,1],vertex[6,1],vertex[1,1]],
			[vertex[0,2],vertex[2,2],vertex[7,2],vertex[1,2],vertex[0,2],vertex[3,2],vertex[6,2],vertex[1,2]],
			c='b',marker=".")
	ax.plot([vertex[5,0],vertex[2,0],vertex[7,0],vertex[4,0],vertex[5,0],vertex[3,0],vertex[6,0],vertex[4,0]],
			[vertex[5,1],vertex[2,1],vertex[7,1],vertex[4,1],vertex[5,1],vertex[3,1],vertex[6,1],vertex[4,1]],
			[vertex[5,2],vertex[2,2],vertex[7,2],vertex[4,2],vertex[5,2],vertex[3,2],vertex[6,2],vertex[4,2]],
			c='b',marker=".")
	return(obb)
def create_aabb(pcd,ax):
	
	aabb=pcd.get_axis_aligned_bounding_box()
	vertex=np.asarray(aabb.get_box_points())
	ax.plot([vertex[0,0],vertex[2,0],vertex[7,0],vertex[1,0],vertex[0,0],vertex[3,0],vertex[6,0],vertex[1,0]],
		[vertex[0,1],vertex[2,1],vertex[7,1],vertex[1,1],vertex[0,1],vertex[3,1],vertex[6,1],vertex[1,1]],
		[vertex[0,2],vertex[2,2],vertex[7,2],vertex[1,2],vertex[0,2],vertex[3,2],vertex[6,2],vertex[1,2]],
		c='b',marker=".")
	ax.plot([vertex[5,0],vertex[2,0],vertex[7,0],vertex[4,0],vertex[5,0],vertex[3,0],vertex[6,0],vertex[4,0]],
		[vertex[5,1],vertex[2,1],vertex[7,1],vertex[4,1],vertex[5,1],vertex[3,1],vertex[6,1],vertex[4,1]],
		[vertex[5,2],vertex[2,2],vertex[7,2],vertex[4,2],vertex[5,2],vertex[3,2],vertex[6,2],vertex[4,2]],
		c='b',marker=".")
	return(aabb)







