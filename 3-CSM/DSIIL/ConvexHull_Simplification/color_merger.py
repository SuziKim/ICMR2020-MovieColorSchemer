#### Call this file under DSIIL
#### python ConvexHull_Simplification/color_merger.py [movie_title]

import numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial import Delaunay
from scipy.optimize import *
from math import *
import cvxopt   
import PIL.Image as Image  
import json, os

import csv
from DSIIL.ConvexHull_Simplification.movie import Movie
import colorsys

######***********************************************************************************************

#### 3D case: use method in paper: "Progressive Hulls for Intersection Applications"
#### also using trimesh.py interface from yotam gingold

def visualize_hull(hull,groundtruth_hull=None):
    from matplotlib import pyplot as plt
    
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(1,1,1, projection='3d')
    vertex=hull.points[hull.vertices]
    ax.scatter(vertex[:,0], vertex[:,1], vertex[:,2], 
       marker='*', color='red', s=40, label='class')
    
#     num=hull.simplices.shape[0]
#     points=[]
#     normals=[]
#     for i in range(num):
#         face=hull.points[hull.simplices[i]]
#         avg_point=(face[0]+face[1]+face[2])/3.0
#         points.append(avg_point)
#     points=np.asarray(points)
    
#     ax.quiver(points[:,0],points[:,1],points[:,2],hull.equations[:,0],hull.equations[:,1],hull.equations[:,2],length=0.01)
    
    for simplex in hull.simplices:
        faces=hull.points[simplex]
        xs=list(faces[:,0])
        xs.append(faces[0,0])
        ys=list(faces[:,1])
        ys.append(faces[0,1])
        zs=list(faces[:,2])
        zs.append(faces[0,2])
#         print xs,ys,zs
        plt.plot(xs,ys,zs,'k-')

    if groundtruth_hull!=None:
        groundtruth_vertex=groundtruth_hull.points[groundtruth_hull.vertices]
        ax.scatter(groundtruth_vertex[:,0], groundtruth_vertex[:,1], groundtruth_vertex[:,2], 
           marker='o', color='green', s=80, label='class')
    
    plt.title("3D Scatter Plot")
    plt.show()
    
    
    
    
from DSIIL.ConvexHull_Simplification.trimesh import TriMesh

def write_convexhull_into_obj_file(hull, output_rawhull_obj_file):
    hvertices=hull.points[hull.vertices]
    points_index=-1*np.ones(hull.points.shape[0],dtype=int)
    points_index[hull.vertices]=np.arange(len(hull.vertices))
    #### start from index 1 in obj files!!!!!
    hfaces=np.array([points_index[hface] for hface in hull.simplices])+1
    
    #### to make sure each faces's points are countclockwise order.
    for index in range(len(hfaces)):
        face=hvertices[hfaces[index]-1]
        normals=hull.equations[index,:3]
        p0=face[0]
        p1=face[1]
        p2=face[2]
        
        n=np.cross(p1-p0,p2-p0)
        if np.dot(normals,n)<0:
            hfaces[index][[1,0]]=hfaces[index][[0,1]]
            
    myfile=open(output_rawhull_obj_file,'w')
    for index in range(hvertices.shape[0]):
        myfile.write('v '+str(hvertices[index][0])+' '+str(hvertices[index][1])+' '+str(hvertices[index][2])+'\n')
    for index in range(hfaces.shape[0]):
        myfile.write('f '+str(hfaces[index][0])+' '+str(hfaces[index][1])+' '+str(hfaces[index][2])+'\n')
    myfile.close()

    


def edge_normal_test(vertices, faces, old_face_index_list, v0_ind, v1_ind):
    selected_old_face_list=[]
    central_two_face_list=[]
    
    for index in old_face_index_list:
        face=faces[index]
        face_temp=np.array(face).copy()
        face_temp=list(face_temp)
        
        if v0_ind in face_temp:
            face_temp.remove(v0_ind)
        if v1_ind in face_temp:
            face_temp.remove(v1_ind)
        if len(face_temp)==2:  ### if left 2 points, then this face is what we need.
            selected_old_face=[np.asarray(vertices[face[i]]) for i in range(len(face))]
            selected_old_face_list.append(np.asarray(selected_old_face))
        if len(face_temp)==1: ##### if left 1 points, then this face is central face.
            central_two_face=[np.asarray(vertices[face[i]]) for i in range(len(face))]
            central_two_face_list.append(np.asarray(central_two_face))
            
    assert( len(central_two_face_list)==2 )
    if len(central_two_face_list)+len(selected_old_face_list)!=len(old_face_index_list):
        print('error!!!!!!')
    
    central_two_face_normal_list=[]
    neighbor_face_dot_normal_list=[]
    
    for face in central_two_face_list:
        n=np.cross(face[1]-face[0], face[2]-face[0])
        n=n/np.sqrt(np.dot(n,n))
        central_two_face_normal_list.append(n)
        
    avg_edge_normal=np.average(np.array(central_two_face_normal_list),axis=0)
    
    for face in selected_old_face_list:
        n=np.cross(face[1]-face[0], face[2]-face[0])
        neighbor_face_dot_normal_list.append(np.dot(avg_edge_normal,n))
    
    if (np.array(neighbor_face_dot_normal_list)>=0.0-1e-5).all():
        return 1
    else:
        return 0


        
def compute_tetrahedron_volume(face, point):
    n=np.cross(face[1]-face[0], face[2]-face[0])
    return abs(np.dot(n, point-face[0]))/6.0




#### this is different from function: remove_one_edge_by_finding_smallest_adding_volume(mesh)
#### add some test conditions to accept new vertex.
#### if option ==1, return a new convexhull.
#### if option ==2, return a new mesh (using trimesh.py)
def remove_one_edge_by_finding_smallest_adding_volume_with_test_conditions(mesh, option):
 
    edges=mesh.get_edges()
    mesh.get_halfedges()
    faces=mesh.faces
    vertices=mesh.vs
    
    temp_list1=[]
    temp_list2=[]
    count=0

    for edge_index in range(len(edges)):
        
        edge=edges[edge_index]
        vertex1=edge[0]
        vertex2=edge[1]
        face_index1=mesh.vertex_face_neighbors(vertex1)
        face_index2=mesh.vertex_face_neighbors(vertex2)

        face_index=list(set(face_index1) | set(face_index2))
        related_faces=[faces[index] for index in face_index]
        old_face_list=[]
        
        
        #### now find a point, so that for each face in related_faces will create a positive volume tetrahedron using this point.
        ### minimize c*x. w.r.t. A*x<=b
        c=np.zeros(3)
        A=[]
        b=[]

        for index in range(len(related_faces)):
            face=related_faces[index]
            p0=vertices[face[0]]
            p1=vertices[face[1]]
            p2=vertices[face[2]]
            old_face_list.append(np.asarray([p0,p1,p2]))
            
            n=np.cross(p1-p0,p2-p0)
            
            #### Currently use this line. without this line, test_fourcolors results are not good.
            n=n/np.sqrt(np.dot(n,n)) ##### use normalized face normals means distance, not volume
            
            A.append(n)
            b.append(np.dot(n,p0))
            c+=n
                

########### now use cvxopt.solvers.lp solver
            
        A=-np.asfarray(A)
        b=-np.asfarray(b)
        
        c=np.asfarray(c)
        cvxopt.solvers.options['show_progress'] = False
        cvxopt.solvers.options['glpk'] = dict(msg_lev='GLP_MSG_OFF')

        res = cvxopt.solvers.lp( cvxopt.matrix(c), cvxopt.matrix(A), cvxopt.matrix(b), solver='glpk' )

        if res['status']=='optimal':
                
            newpoint = np.asfarray( res['x'] ).squeeze()
        

            ######## using objective function to calculate (volume) or (distance to face) as priority.
#             volume=res['primal objective']+b.sum()
            
    
            ####### manually compute volume as priority,so no relation with objective function
            tetra_volume_list=[]
            for each_face in old_face_list:
                tetra_volume_list.append(compute_tetrahedron_volume(each_face,newpoint))
            volume=np.asarray(tetra_volume_list).sum()
            


            temp_list1.append((count, volume, vertex1, vertex2))
            temp_list2.append(newpoint)
            count+=1
           
        # else:
        #     print 'cvxopt.solvers.lp is not optimal ', res['status'], np.asfarray( res['x'] ).squeeze()
        #     if res['status']!='unknown': ### means solver failed
        #         ##### check our test to see if the solver fails normally
        #         if edge_normal_test(vertices,faces,face_index,vertex1,vertex2)==1: ### means all normal dot value are positive
        #             print '!!!edge_normal_neighbor_normal_dotvalue all positive, but solver fails'
              
                

    if option==1:
        if len(temp_list1)==0:
            print('all fails')
            hull=ConvexHull(mesh.vs)
        else:
            min_tuple=min(temp_list1,key=lambda x: x[1])
            # print min_tuple
            final_index=min_tuple[0]
            final_point=temp_list2[final_index]
            # print 'final_point ', final_point
            new_total_points=mesh.vs
            new_total_points.append(final_point)

            hull=ConvexHull(np.array(new_total_points))
        return hull
    
    if option==2:
        
        if len(temp_list1)==0:
            print('all fails')
        else:
            min_tuple=min(temp_list1,key=lambda x: x[1])
            # print min_tuple
            final_index=min_tuple[0]
            final_point=temp_list2[final_index]
            # print 'final_point ', final_point
            
            v1_ind=min_tuple[2]
            v2_ind=min_tuple[3]
            
            face_index1=mesh.vertex_face_neighbors(v1_ind)
            face_index2=mesh.vertex_face_neighbors(v2_ind)

            face_index=list(set(face_index1) | set(face_index2))
            related_faces_vertex_ind=[faces[index] for index in face_index]
            
            old2new=mesh.remove_vertex_indices([v1_ind, v2_ind])
            
            ### give the index to new vertex.
            new_vertex_index=current_vertices_num=len(old2new[old2new!=-1])
            
            ### create new face with new vertex index.
            new_faces_vertex_ind=[]
            
            for face in related_faces_vertex_ind:
                new_face=[new_vertex_index if x==v1_ind or x==v2_ind else old2new[x] for x in face]
                if len(list(set(new_face)))==len(new_face):
                    new_faces_vertex_ind.append(new_face)
            
            

            ##### do not clip coordinates to[0,255]. when simplification done, clip.
            mesh.vs.append(final_point)
            

            ##### clip coordinates during simplification!
            # mesh.vs.append(final_point.clip(0.0,255.0))
            

            for face in new_faces_vertex_ind:
                mesh.faces.append(face)
            mesh.topology_changed()
    
        return mesh
        

    
def save_palette_image(pigments_colors, path, shouldSave=True):
    hls_pigments_colors = np.array([tuple(colorsys.rgb_to_hls(pc[0][0]/255, pc[0][1]/255, pc[0][2]/255)) for pc in pigments_colors], dtype=[('h', float), ('l', float), ('s', float)])
    hls_pigments_colors.sort(order=['h', 'l', 's'])
    hls_pigments_colors = hls_pigments_colors[::-1]

    rgb_pigments_colors = np.rint([[e*255 for e in colorsys.hls_to_rgb(pc[0], pc[1], pc[2])] for pc in hls_pigments_colors])

    width = 100
    # rgb_pigments_colors_box_15 = rgb_pigments_colors.reshape((int(rgb_pigments_colors.shape[0]/15), 15, rgb_pigments_colors.shape[1]))
    # rgb_pigments_colors_box_15 = rgb_pigments_colors_box_15.astype('uint8')

    rgb_pigments_colors_box_10 = rgb_pigments_colors.reshape((int(rgb_pigments_colors.shape[0]/10), 10, rgb_pigments_colors.shape[1]))
    rgb_pigments_colors_box_10 = rgb_pigments_colors_box_10.astype('uint8')

    # bulked_up = np.repeat(np.repeat(np.moveaxis(rgb_pigments_colors_box_15, 0, 1), width, 0), width, 1)
    # Image.fromarray( np.transpose(bulked_up, [1,0,2]) ).save(path.replace('.png', '-15-box.tiff'), dpi=(500,500))

    white_width = 5
    # for i in reversed(range(1,15)):
    #     bulked_up = np.insert(bulked_up, [i*width for k in range(white_width)], [255], axis=0)
    # for i in reversed(range(1, int(rgb_pigments_colors.shape[0]/15))):
    #     bulked_up = np.insert(bulked_up, [i*width for k in range(white_width)], [255], axis=1)

    # Image.fromarray( np.transpose(bulked_up, [1,0,2]) ).save(path.replace('.png', '-15-w-box.tiff'), dpi=(500,500))

    bulked_up = np.repeat(np.repeat(np.moveaxis(rgb_pigments_colors_box_10, 0, 1), width, 0), width, 1)
    Image.fromarray( np.transpose(bulked_up, [1,0,2]) ).save(path.replace('.png', '-10-box.tiff'), dpi=(500,500))

    for i in reversed(range(1,10)):
        bulked_up = np.insert(bulked_up, [i*width for k in range(white_width)], [255], axis=0)
    for i in reversed(range(1,int(rgb_pigments_colors.shape[0]/10))):
        bulked_up = np.insert(bulked_up, [i*width for k in range(white_width)], [255], axis=1)

    Image.fromarray( np.transpose(bulked_up, [1,0,2]) ).save(path.replace('.png', '-10-w-box.tiff'), dpi=(500,500))

    rgb_pigments_colors = rgb_pigments_colors.reshape((int(rgb_pigments_colors.shape[0]), 1, rgb_pigments_colors.shape[1]))
    rgb_pigments_colors = rgb_pigments_colors.astype('uint8')

    bulked_up = np.repeat(np.repeat(np.moveaxis(rgb_pigments_colors, 0, 1), width, 0), width, 1)
    Image.fromarray( bulked_up ).save(path, dpi=(500,500))

    print(np.shape(bulked_up))
    for i in reversed(range(1,len(pigments_colors))):
        bulked_up = np.insert(bulked_up, [i*width for k in range(white_width)], [255], axis=1)

    Image.fromarray( bulked_up ).save(path.replace('.png', '-w.tiff'), dpi=(500,500))
    return rgb_pigments_colors
    

# movie_title: ex) in_the_mood_for_love, la_la_land     
# jitter_offset: same or larger than zero
def merge_colors(movie_title, dataset_type, jitter_offset):

    # Experiments constraints
    should_jitter_colors = True
    fixed_color_counts = 30

    # read basic movie info
    movie = Movie(movie_title, dataset_type, should_jitter_colors, jitter_offset)
    movie.read_shot_information()

    # read color info from movie
    movie.read_shot_colors(0.5, 0.8, 6) 

    import os

    # Generate a directory to save the result
    output_dir_path = os.path.join('..', 'results', 'color_schemes', dataset_type, movie_title)
    try:
        if not(os.path.isdir(output_dir_path)):
            os.makedirs(output_dir_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create directory!!!!!")
            raise

    output_rawhull_obj_file = os.path.join(output_dir_path, movie_title +(("_nche_o-%d-rawconvexhull.obj") % jitter_offset))
    js_output_file = os.path.join(output_dir_path, movie_title +(("_nche_o-%d-final_simplified_hull.js") % jitter_offset))
    js_output_clip_file = os.path.join(output_dir_path, movie_title +(("_nche_o-%d-final_simplified_hull_clip.js") % jitter_offset))
    js_output_file_origin = os.path.join(output_dir_path, movie_title +(("_nche_o-%d-original_hull.js") % jitter_offset))
    E_vertice_num = fixed_color_counts + 10

    # images=np.asfarray(Image.open(input_image_path).convert('RGB')).reshape((-1,3))
    # images = np.asfarray(movie.weighted_shot_colors)
    images = np.asfarray(movie.shot_colors)
    images_reshaped = images.reshape(images.shape[0], 1, images.shape[1]).astype('uint8')
    width = 20
    # images_reshaped = np.repeat(np.repeat(images_reshaped, width, 1), width, 0)
    
    w, h, c= images_reshaped.shape
    squared_size = ceil(sqrt(w)) * width
    squared_images = np.zeros((squared_size, squared_size, c+1))
    for i in range(images_reshaped.shape[0]):
        co = floor(i / ceil(sqrt(w)))
        ro = i % ceil(sqrt(w))
        for row in range(ro*width, (ro+1) * width):
            for col in range(co*width, (co+1) * width):
                squared_images[col][row][0] = images_reshaped[i][0][0]
                squared_images[col][row][1] = images_reshaped[i][0][1]
                squared_images[col][row][2] = images_reshaped[i][0][2]
                squared_images[col][row][3] = 255

    squared_images = Image.fromarray( squared_images.astype('uint8') )
    squared_images.save(os.path.splitext(js_output_clip_file)[0] + '-original_unweighted_image.png')

    wimages = np.asfarray(movie.weighted_shot_colors)
    images_reshaped = wimages.reshape(wimages.shape[0], 1, wimages.shape[1]).astype('uint8')
    width = 1
    images_reshaped = np.repeat(np.repeat(images_reshaped, width, 1), width, 0)

    w, h, c= images_reshaped.shape
    squared_size = ceil(sqrt(w*h))
    squared_images = np.zeros((squared_size, squared_size, c+1))

    row = 0
    col = 0
    for i in range(images_reshaped.shape[0]):
        row = floor(i / squared_size)
        col = i % squared_size
        squared_images[row][col][0] = images_reshaped[i][0][0]
        squared_images[row][col][1] = images_reshaped[i][0][1]
        squared_images[row][col][2] = images_reshaped[i][0][2]
        squared_images[row][col][3] = 255

    squared_images = Image.fromarray( squared_images.astype('uint8') )
    squared_images.save(os.path.splitext(js_output_clip_file)[0] + '-original_weighted_image.png')

    # shape of images: (k, 3) / [0 255]
    hull=ConvexHull(images)
    origin_hull=hull
    # visualize_hull(hull)
    write_convexhull_into_obj_file(hull, output_rawhull_obj_file)

    pigments_colors = None
    use_sphere = False

    N=500
    mesh=TriMesh.FromOBJ_FileName(output_rawhull_obj_file)
    print('original vertices number:',len(mesh.vs))

    newhull = hull
    for i in range(N):

        # print 'loop:', i
        
        old_num=len(mesh.vs)
        mesh=TriMesh.FromOBJ_FileName(output_rawhull_obj_file)
        mesh=remove_one_edge_by_finding_smallest_adding_volume_with_test_conditions(mesh,option=2)
        newhull=ConvexHull(mesh.vs)
        write_convexhull_into_obj_file(newhull, output_rawhull_obj_file)

        # print 'current vertices number:', len(mesh.vs)

        if len(newhull.simplices) == E_vertice_num+1:
            name = os.path.splitext( js_output_file )[0] + ( '-%02d.js' % len(newhull.vertices ))
            with open( name, 'w' ) as myfile:
                json.dump({'vs': newhull.points[ newhull.vertices ].tolist(),'faces': newhull.points[ newhull.simplices ].tolist()}, myfile, indent = 4 )
            
            name = os.path.splitext( js_output_clip_file )[0] + ( '-%02d.js' % len(newhull.vertices ))
            with open( name, 'w' ) as myfile:
                json.dump({'vs': newhull.points[ newhull.vertices ].clip(0.0,255.0).tolist(),'faces': newhull.points[ newhull.simplices ].clip(0.0,255.0).tolist()}, myfile, indent = 4 )
            
            pigments_colors=newhull.points[ newhull.vertices ].clip(0,255).round().astype(np.uint8)
            np.savetxt(os.path.splitext( js_output_clip_file )[0] + ( '-%02d.txt' % len(newhull.vertices )), pigments_colors, fmt='%d')

            pigments_colors=pigments_colors.reshape((pigments_colors.shape[0],1,pigments_colors.shape[1]))
            # Image.fromarray( pigments_colors ).save( os.path.splitext( js_output_clip_file )[0] + ( '-%02d.png' %save_palette_image len(newhull.vertices )) )
            # pigments_colors = save_palette_image(pigments_colors, \
                # os.path.splitext( js_output_clip_file )[0] + ( '-jitter-%02d.png' % len(newhull.vertices )))

        if len(mesh.vs) == old_num or len(newhull.simplices) <= E_vertice_num:
            pigments_colors=newhull.points[ newhull.vertices ].clip(0,255).round().astype(np.uint8)
            np.savetxt(os.path.splitext( js_output_clip_file )[0] + ( '-%02d.txt' % len(newhull.vertices )), pigments_colors, fmt='%d')

            pigments_colors=pigments_colors.reshape((pigments_colors.shape[0],1,pigments_colors.shape[1]))
            # Image.fromarray( pigments_colors ).save( os.path.splitext( js_output_clip_file )[0] + ( '-%02d.png' %save_palette_image len(newhull.vertices )) )
            # pigments_colors = save_palette_image(pigments_colors, \
                # os.path.splitext( js_output_clip_file )[0] + ( '-jitter-%02d.png' % len(newhull.vertices )), False)

            print('final vertices number: ', len(mesh.vs), '/ face numbers: ', len(newhull.simplices))
            break

    # print(pigments_colors)

    # re-clustering
    # image : np array with all color
    # pigments_colors: array with centers

    n_pigments_colors = []
    if use_sphere:
        color_covered = []
        for i in range(len(movie.shot_colors)):
            color_covered.append(0)

        for c in pigments_colors:
            # 1. filtering target colors in image
            print(c)
            print('\tfiltering target colors in image')
            target_colors = []
            target_weights = []

            for idx in range(len(movie.shot_colors)):
                c_ = movie.shot_colors[idx]
                dist = np.linalg.norm(np.array(c) - np.array(c_))
                if dist < 255/10:
                    target_colors.append(c_)
                    target_weights.append(movie.weights[idx])
                    color_covered[idx] = 1

            # 2. find weighted center point
            print('\tfind weighted center point among ', len(target_colors), ' colors')
            x = 0
            y = 0
            z = 0
            totalCounts = 0
            for idx in range(len(target_colors)):
                x += target_colors[idx][0] * target_weights[idx]
                y += target_colors[idx][1] * target_weights[idx]
                z += target_colors[idx][2] * target_weights[idx]
                totalCounts += target_weights[idx]

            x /= totalCounts
            y /= totalCounts
            z /= totalCounts

            # 3. find closest center point
            print('\tfind closest center point of (', x, y, z, ')')
            closestDistance = inf
            closestPoint = None
            for c_ in target_colors:
                dist = np.linalg.norm(np.array(c_) - np.array([x, y, z]))
                if dist < closestDistance:
                    if c_ not in n_pigments_colors:
                        closestDistance = dist
                        closestPoint = c_

            if closestPoint is None:
                print('target: ', target_colors)
                print('pigment: ', n_pigments_colors)

            print('\tclosest: ', closestPoint)
            n_pigments_colors.append(closestPoint)


        uncovered = []
        uncovered_weight = []
        for idx in range(len(color_covered)):
            if color_covered[idx] == 0:
                uncovered.append(movie.shot_colors[idx])
                uncovered_weight.append(movie.weights[idx])
        print('Uncovred area: ', len(uncovered))

        x = 0
        y = 0
        z = 0
        totalCounts = 0
        for idx in range(len(uncovered)):
            x += uncovered[idx][0] * uncovered_weight[idx]
            y += uncovered[idx][1] * uncovered_weight[idx]
            z += uncovered[idx][2] * uncovered_weight[idx]
            totalCounts += uncovered_weight[idx]

        x /= totalCounts
        y /= totalCounts
        z /= totalCounts
        print('\tweighted center: ', x, y, z)

        closestDistance = inf
        closestPoint = None
        for c_ in uncovered:
            dist = np.linalg.norm(np.array(c_) - np.array([x, y, z]))
            if dist < closestDistance:
                if c_ not in n_pigments_colors:
                    closestDistance = dist
                    closestPoint = c_

        n_pigments_colors.append(closestPoint)
        print('\tcolor from uncovered: ', closestPoint)
        print(n_pigments_colors)
        n_pigments_colors = np.array(n_pigments_colors)
        np.savetxt(os.path.splitext( js_output_clip_file )[0] + '-30-nCHE.txt', n_pigments_colors, fmt='%d')
        n_pigments_colors = n_pigments_colors.reshape((n_pigments_colors.shape[0],1,n_pigments_colors.shape[1]))
        n_pigments_colors = save_palette_image(n_pigments_colors, \
                    os.path.splitext( js_output_clip_file )[0] + '-nche-w-uncovered.png')

        return n_pigments_colors

    else:
        use_weighted_center = False
        centerPoint = [0, 0, 0]
        totalCounts = 0
        if use_weighted_center:
            # calculate weighted center
            for idx in range(len(movie.shot_colors)):
                centerPoint[0] += movie.shot_colors[idx][0] * movie.weights[idx]
                centerPoint[1] += movie.shot_colors[idx][1] * movie.weights[idx]
                centerPoint[2] += movie.shot_colors[idx][2] * movie.weights[idx]
                totalCounts += movie.weights[idx]
        else:
            # calculate general center
            for idx in range(len(movie.shot_colors)):
                centerPoint[0] += movie.shot_colors[idx][0]
                centerPoint[1] += movie.shot_colors[idx][1]
                centerPoint[2] += movie.shot_colors[idx][2]
                totalCounts += 1
        
        centerPoint[0] /= totalCounts
        centerPoint[1] /= totalCounts
        centerPoint[2] /= totalCounts

        # define Face List
        subhulls = []
        clusters = []
        clusters_weights = []
        faceList = []
        for simplex in newhull.simplices:
            subhull = [newhull.points[vid] for vid in simplex]
            subhull.append(np.array(centerPoint))
            subhulls.append(subhull)
            clusters.append([])
            clusters_weights.append([])

            subFaceList = []
            for i in range(3):
                subFaceList.append(np.array(centerPoint))
                if i == 2:
                    subFaceList.append(newhull.points[simplex[i]])
                    subFaceList.append(newhull.points[simplex[0]])
                else:
                    subFaceList.append(newhull.points[simplex[i]])
                    subFaceList.append(newhull.points[simplex[i+1]])

            faceList.append(subFaceList)

        name = os.path.splitext( js_output_clip_file )[0] + ( '-ch-%02d.js' % len(newhull.vertices ))
        with open( name, 'w' ) as myfile:
            json.dump({'vs': newhull.points[ newhull.vertices ].clip(0.0,255.0).tolist(),'faces': newhull.points[ newhull.simplices ].clip(0.0,255.0).tolist()}, myfile, indent = 4 )

        faceList = np.array(faceList)
        name = os.path.splitext( js_output_clip_file )[0] + ( '-subhull-%02d.js' % len(newhull.vertices ))
        with open( name, 'w' ) as myfile:
            json.dump({'vs': newhull.points[ newhull.vertices ].clip(0.0,255.0).tolist() + [centerPoint],'faces': newhull.points[ newhull.simplices ].clip(0.0,255.0).tolist() + faceList.clip(0,255).tolist()}, myfile, indent = 4 )

        # make cluster 
        for cidx in range(len(movie.shot_colors)):
            c_ = movie.shot_colors[cidx]
            included = False
            for shidx in range(len(subhulls)):
                if pnt_in_cvex_hull(subhulls[shidx], c_):
                    clusters[shidx].append(c_)
                    clusters_weights[shidx].append(movie.weights[cidx])
                    included = True
                    break

            if included is False:
                print("**************not included! ", c_)
                error()

        for idx in range(len(clusters)):
            print('cluster #', idx, ' count: ', len(clusters[idx]))

        sorted_clusters = sorted(clusters, key=len, reverse=True)
        index_array = sorted(range(len(clusters)), key=lambda k: len(clusters[k]), reverse=True)
        sorted_weights = [clusters_weights[k] for k in index_array]
        sorted_clusters = sorted_clusters[:fixed_color_counts]
        if len(sorted_clusters[-1]) == 0:
            print("********** zero cluster happened..")
            error()

        for clusterIdx in range(len(sorted_clusters)):
            cluster_centerPoint = [0, 0, 0]
            totalCounts = 0
            for idx in range(len(sorted_clusters[clusterIdx])):
                cluster_centerPoint[0] += sorted_clusters[clusterIdx][idx][0] * sorted_weights[clusterIdx][idx]
                cluster_centerPoint[1] += sorted_clusters[clusterIdx][idx][1] * sorted_weights[clusterIdx][idx]
                cluster_centerPoint[2] += sorted_clusters[clusterIdx][idx][2] * sorted_weights[clusterIdx][idx]
                totalCounts += sorted_weights[clusterIdx][idx]

            cluster_centerPoint[0] /= totalCounts
            cluster_centerPoint[1] /= totalCounts
            cluster_centerPoint[2] /= totalCounts

            # 3. find closest center point
            print('\tfind closest center point of ', cluster_centerPoint)
            closestDistance = inf
            closestPoint = None
            for c_ in sorted_clusters[clusterIdx]:
                dist = np.linalg.norm(np.array(c_) - np.array(cluster_centerPoint))
                if dist < closestDistance:
                    closestDistance = dist
                    closestPoint = c_
            n_pigments_colors.append(closestPoint)

        n_pigments_colors = np.array(n_pigments_colors)
        np.savetxt(os.path.splitext( js_output_clip_file )[0] + '-30-nCHE.txt', n_pigments_colors, fmt='%d')
        n_pigments_colors = n_pigments_colors.reshape((n_pigments_colors.shape[0],1,n_pigments_colors.shape[1]))
        n_pigments_colors = save_palette_image(n_pigments_colors, \
                    os.path.splitext( js_output_clip_file )[0] + '-nche-w-uncovered.png')

        return n_pigments_colors

def pnt_in_cvex_hull(hullpoints, pnt):
    '''
    Checks if `pnt` is inside the convex hull.
    `hull` -- a QHull ConvexHull object
    `pnt` -- point array of shape (3,)
    '''
    hull = ConvexHull(hullpoints, incremental=True)
    new_hull = ConvexHull(np.concatenate((hull.points, [pnt])), incremental = True)
    # print("volume: ", hull.volume, new_hull.volume, abs(hull.volume-new_hull.volume) < 1.0)
    if np.array_equal(new_hull.vertices, hull.vertices) or abs(hull.volume-new_hull.volume) < 1.0: 
        return True
    return False

# def pnt_in_cvex_hull(hullpoints, pnt):
#     '''
#     Given a set of points that defines a convex hull, uses simplex LP to determine
#     whether point lies within hull.
#     `hull_points` -- (N, 3) array of points defining the hull
#     `pnt` -- point array of shape (3,)
#     '''
#     N = len(hullpoints)
#     c = np.ones(N)
#     A_eq = np.concatenate((hullpoints, np.ones((N,1))), 1).T   # rows are x, y, z, 1
#     b_eq = np.concatenate((pnt, (1,)))
#     result = linprog(c, A_eq=A_eq, b_eq=b_eq)
#     if result.success and c.dot(result.x) == 1.:
#         return True
#     return False