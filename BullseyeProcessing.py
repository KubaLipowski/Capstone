"""
Created on Tues Mar 2 21:29:28 2021

@author: Kuba Lipowski

Image processing tool for annular analysis of blood vessels
"""

from PIL import Image
import numpy as np
import cv2
import math
from shapely.geometry import Point as pt
from shapely.geometry import Polygon
from math import atan2
import matplotlib.pyplot as plt
from datetime import datetime


#detailed function responsible for annular analysis
def bullseye(filename1,filename2,my_window,directory,scale):
    global image,mask,image_to_show,mask_to_show,rings_to_show,mouse_pressed,s_x,s_y,e_x,e_y,drawing,mode,points,timestamp
    Image.MAX_IMAGE_PIXELS = None
    image = cv2.imread(filename1)
    mask = cv2.imread(filename2)
    image_to_show = np.copy(image)
    mask_to_show = np.copy(mask)
    rings_to_show = np.copy(mask)
    mouse_pressed = False
    timestamp = datetime.now().strftime("%Y_%m_%d_%I-%M-%S")
    #s_x = s_y = e_x = e_y = -1
    drawing=False # true if mouse is pressed
    mode=True # if True, draw rectangle. Press 'm' to toggle to curve
    points = list()


    #Class that defines centroids of nuclei
    class Point:
        x = 0.0
        y = 0.0
        def make_point(self,current_x,current_y):
            self.x = current_x
            self.y = current_y


    def getAngle(p1,ring):
        dx = ring[0]-p1.x
        dy = ring[1]-p1.y
        return atan2(dy,dx)-math.pi


    #returns area of polygon
    def ring_area(ring_coords):
        poly = Polygon(ring_coords)
        x,y = poly.exterior.xy
        return ((1/1.552)**2)*0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))


    #returns centroid of nuclei
    def get_centroid(points):
        length = len(points)
        sum_x = 0
        sum_y = 0
        for i in range(len(points)):
            sum_x = sum_x + points[i].x
            sum_y = sum_y + points[i].y
        return sum_x/length, sum_y/length


    #returns the coordinates of the centroids of each nucleus in array of coordinates
    def count_nuclei():
        imgray = cv2.cvtColor(rings_to_show,cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(imgray,127,255,cv2.THRESH_BINARY)

        # Find contours, draw on image and save
        contours = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]
        #cv2.drawContours(mask_to_show, contours, -1, (0,255,0), 1)
        cell_counts = []

        #show user what we found
        centers = []
        s1, s2 = 10, 20000
        for cell in contours:
            (x,y),radius = cv2.minEnclosingCircle(cell)
            if s1<cv2.contourArea(cell)<s2:
                cell_counts.append(cell)
                center = (int(x),int(y))
                centers.append(center)
                radius = int(radius)
                im = cv2.circle(mask_to_show, (int(x),int(y)), 2, (0,0,255), 2)
        #cv2.imwrite('result.png',mask_to_show)

        return centers


    #returns the number of nuclei found in each ring
    def get_ring_counts(centers, points, ring1_coords, ring2_coords, ring3_coords, ring4_coords):
        ring1 = Polygon(ring1_coords)
        ring2 = Polygon(ring2_coords)
        ring3 = Polygon(ring3_coords)
        ring4 = Polygon(ring4_coords)

        ring1_count, ring2_count, ring3_count, ring4_count = 0,0,0,0
        for p in centers:
            cell = pt(p[0], p[1])
            if check_inside_ring(ring1, cell):
                ring1_count = ring1_count + 1
            if check_inside_ring(ring2, cell):
                ring2_count = ring2_count + 1
            if check_inside_ring(ring3, cell):
                ring3_count = ring3_count + 1
            if check_inside_ring(ring4, cell):
                ring4_count = ring4_count + 1
        all_rings = ring4_count
        ring4_count = ring4_count - ring3_count
        ring3_count = ring3_count - ring2_count
        ring2_count = ring2_count - ring1_count
        return ring1_count,ring2_count,ring3_count,ring4_count, all_rings


    #returns whether or not a nucleus is within a specified ring
    def check_inside_ring(ring, cell):
        if ring.contains(cell):
            return True
        return False


    #mouse input corresponds to cropping the image
    def mouse_callback(event, x, y, flags, param):
        global image_to_show, s_x, s_y, e_x, e_y, mouse_pressed
        global mask_to_show, rings_to_show, s_x, s_y, e_x, e_y, mouse_pressed
        if event == cv2.EVENT_LBUTTONDOWN:
            mouse_pressed = True
            s_x, s_y = x, y
            image_to_show = np.copy(image)
            mask_to_show = np.copy(mask)
            rings_to_show = np.copy(mask)

        elif event == cv2.EVENT_MOUSEMOVE:
            if mouse_pressed:
                image_to_show = np.copy(image)
                mask_to_show = np.copy(mask)
                rings_to_show = np.copy(mask)
                rings_to_show = np.copy(mask)
                cv2.rectangle(image_to_show, (s_x, s_y),
                              (x, y), (0, 255, 0), 1)
                cv2.rectangle(mask_to_show, (s_x, s_y),
                              (x, y), (0, 255, 0), 1)
                cv2.rectangle(rings_to_show, (s_x, s_y),
                              (x, y), (0, 255, 0), 1)
        elif event == cv2.EVENT_LBUTTONUP:
            mouse_pressed = False
            e_x, e_y = x, y


    # mouse callback function for tracing the vessel
    def begueradj_draw(event,former_x,former_y,flags,param):
        global current_former_x,current_former_y,drawing, mode
        if event==cv2.EVENT_LBUTTONDOWN:
            drawing=True
            current_former_x,current_former_y=former_x,former_y

        elif event==cv2.EVENT_MOUSEMOVE:
            if drawing==True:
                if mode==True:
                    cv2.line(image_to_show,(current_former_x,current_former_y),(former_x,former_y),(0,0,255),5)
                    cv2.line(mask_to_show,(current_former_x,current_former_y),(former_x,former_y),(0,0,255),5)
                    p = Point()
                    p.make_point(former_x,former_y)
                    points.append(p)
                    current_former_x = former_x
                    current_former_y = former_y

        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            if mode == True:
                cv2.line(image_to_show,(current_former_x,current_former_y),(former_x,former_y),(0,0,255),5)
                cv2.line(mask_to_show,(current_former_x,current_former_y),(former_x,former_y),(0,0,255),5)
                current_former_x = former_x
                current_former_y = former_y
        return former_x,former_y

    cv2.namedWindow(my_window, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(my_window, mouse_callback)

    while cv2.getWindowProperty(my_window,0)>=0:
        cv2.imshow(my_window, image_to_show)
        k = cv2.waitKey(1)
        if k == ord('c'):
            if s_y > e_y:
                s_y, e_y = e_y, s_y
            if s_x > e_x:
                s_x, e_x = e_x, s_x

            if e_y - s_y > 1 and e_x - s_x > 0:
                image = image[s_y:e_y, s_x:e_x]
                mask = mask[s_y:e_y, s_x:e_x]
                image_to_show = np.copy(image)
                mask_to_show = np.copy(mask)
                rings_to_show = np.copy(mask)
        elif k == ord('p'):
            cv2.setMouseCallback(my_window,begueradj_draw)
        elif k == ord('q'):
            center = get_centroid(points)
            j = 1
            ring1_coords = []
            ring2_coords = []
            ring3_coords = []
            ring4_coords = []
            for i in range(len(points)-1):
                x_distance1 = (points[j-1].x-center[0])
                y_distance1 = (points[j-1].y-center[1])
                x_distance2 = (points[j].x-center[0])
                y_distance2 = (points[j].y-center[1])
                hypotenuse = 100
                ring1_coords.append((points[j-1].x,points[j-1].y))
                angle1 = getAngle(points[j-1],center)
                ring2_coords.append((int((math.cos(angle1))*hypotenuse+points[j-1].x),int((math.sin(angle1))*hypotenuse+points[j-1].y)))
                angle2 = angle1#getAngle(points[j-1],ring2_coords[j-1])
                ring3_coords.append((round(math.cos(angle2)*hypotenuse+ring2_coords[j-1][0]),round(math.sin(angle2)*hypotenuse+ring2_coords[j-1][1])))
                angle3 = angle1#getAngle(points[j-1],ring3_coords[j-1])
                ring4_coords.append((round(math.cos(angle3)*hypotenuse+ring3_coords[j-1][0]),round(math.sin(angle3)*hypotenuse+ring3_coords[j-1][1])))
                j = j+1
            j = 1
            for i in range(len(ring1_coords)-1):
                cv2.line(image_to_show,(ring2_coords[j-1][0],ring2_coords[j-1][1]),(ring2_coords[j][0],ring2_coords[j][1]),(0,200,255),3)
                cv2.line(image_to_show,(ring3_coords[j-1][0],ring3_coords[j-1][1]),(ring3_coords[j][0],ring3_coords[j][1]),(0,100,255),3)
                cv2.line(image_to_show,(ring4_coords[j-1][0],ring4_coords[j-1][1]),(ring4_coords[j][0],ring4_coords[j][1]),(0,50,255),3)
                cv2.line(mask_to_show,(ring2_coords[j-1][0],ring2_coords[j-1][1]),(ring2_coords[j][0],ring2_coords[j][1]),(0,200,255),3)
                cv2.line(mask_to_show,(ring3_coords[j-1][0],ring3_coords[j-1][1]),(ring3_coords[j][0],ring3_coords[j][1]),(0,100,255),3)
                cv2.line(mask_to_show,(ring4_coords[j-1][0],ring4_coords[j-1][1]),(ring4_coords[j][0],ring4_coords[j][1]),(0,50,255),3)
                j = j+1
        elif k == 27:
            break

    cv2.imwrite(directory+'/my_images/original_'+timestamp+'.png',image_to_show)

    while True:
        k = cv2.waitKey(1)
        centers = count_nuclei()
        ring1_count,ring2_count,ring3_count,ring4_count,all_rings = get_ring_counts(centers, points, ring1_coords, ring2_coords, ring3_coords, ring4_coords)
        #1 um = 1.55 pixels
        area1 = ring_area(ring1_coords)
        area2 = ring_area(ring2_coords) - ring_area(ring1_coords)
        area3 = ring_area(ring3_coords) - ring_area(ring2_coords)
        area4 = ring_area(ring4_coords) - ring_area(ring3_coords)
        break
    #print('Ring 1 density: {} nuc/um^2\nRing 2 density: {} nuc/um^2\nRing 3 density: {} nuc/um^2\nRing 4 density: {} nuc/um^2\nTotal count: {} nuc, Lumen: {} um^2'.format(ring1_count/area1,ring2_count/area2,ring3_count/area3,ring4_count/area4,all_rings,area1))
    densities = np.array([str(ring1_count/area1),str(ring2_count/area2),str(ring3_count/area3),str(ring4_count/area4),str(area1)])
    #file_obj = open(r"ring_count_data_d1.txt","a")
    return centers, points, ring1_coords, ring2_coords, \
           ring3_coords, ring4_coords, ring1_count, \
           ring2_count, ring3_count, ring4_count, \
           all_rings, round(area1), timestamp


#counts cells across full tissue section
def global_count(filename,day,stain):
    cell_counts = []
    centers = []
    for i in range(1,82):
        specific_filename = filename + '/Day' + day + '/' + stain + ' Mask/'+'tile_'+str(i)+'_mask.tif'
        print(specific_filename)
        image = cv2.imread(specific_filename)
        imgray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(imgray,127,255,cv2.THRESH_BINARY)
        print(specific_filename)
        # Find contours, draw on image and save
        contours = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]
        #cv2.drawContours(mask_to_show, contours, -1, (0,255,0), 1)
        s1, s2 = 0, 20000
        for cell in contours:
            (x,y),radius = cv2.minEnclosingCircle(cell)
            if s1<cv2.contourArea(cell)<s2:
                cell_counts.append(cell)
                center = (int(x),int(y))
                centers.append(center)
                radius = int(radius)
    print(len(centers))
    return len(centers)


#scales coords to be in microns
def normalize_rings(ring_coords):
    pixels = [(pixel[0]/1.55, pixel[1]/1.55) for pixel in ring_coords]
    return pixels


def scale_plot(x,y,minx,miny):
    x = [(value - minx + 100) for value in x]
    y = [(value - miny + 100) for value in y]
    return x,y

#creates schematic representation of annular analysis
def plot_signal(centers, ring1_coords, ring2_coords, ring3_coords, ring4_coords, title,directory):
    nring1_coords = normalize_rings(ring1_coords)
    nring2_coords = normalize_rings(ring2_coords)
    nring3_coords = normalize_rings(ring3_coords)
    nring4_coords = normalize_rings(ring4_coords)

    ring1 = Polygon(nring1_coords)
    ring2 = Polygon(nring2_coords)
    ring3 = Polygon(nring3_coords)
    ring4 = Polygon(nring4_coords)

    x,y = ring1.exterior.xy
    x1,y1 = ring2.exterior.xy
    x2,y2 = ring3.exterior.xy
    x3,y3 = ring4.exterior.xy

    minx = min(x3)
    miny = min(y3)
    x,y = scale_plot(x,y,min(x3),min(y3))
    x1,y1 = scale_plot(x1,y1,min(x3),min(y3))
    x2,y2 = scale_plot(x2,y2,min(x3),min(y3))
    x3,y3 = scale_plot(x3,y3,min(x3),min(y3))

    xx = []
    yy = []
    centers = normalize_rings(centers)
    for cent in centers:
        xx.append(cent[0])
        yy.append(cent[1])
    xx,yy = scale_plot(xx,yy,minx,miny)
    yy_mid = round(np.max(yy))
    for i in range(0,len(xx)):
        yy[i] = yy[i]+2*abs(yy_mid-yy[i])
    for i in range (0,len(x)):
        y[i] = y[i]+2*abs(yy_mid-y[i])
        y1[i] = y1[i]+2*abs(yy_mid-y1[i])
        y2[i] = y2[i]+2*abs(yy_mid-y2[i])
        y3[i] = y3[i]+2*abs(yy_mid-y3[i])
    plt.plot(x, y)
    plt.plot(x1, y1)
    plt.plot(x2, y2)
    plt.plot(x3, y3)
    plt.scatter(xx, yy, s=5)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.xlabel('Distance (um)',fontsize=20)
    plt.ylabel('Distance (um)',fontsize=20)
    plt.title(title,fontsize=20)
    plt.ylim(min(y3)-100,max(y3)+100)
    plt.xlim(min(x3)-100,max(x3)+100)
    plt.savefig(directory+'/my_images/schematic_'+timestamp+'.png')
    plt.clf()


#main function used for rapid testing
def main():
    filename1 = 'MergedTile.tif'
    filename2 = 'ED1_d6.tif'
    centers, points, ring1_coords, ring2_coords, ring3_coords, ring4_coords,r1, r2,r3,r4,nuclei_count,lumen,time = bullseye(filename1,filename2,'mask','C:/Users/student/Desktop/PC Lab',10)
    p = plot_signal(centers, ring1_coords, ring2_coords, ring3_coords, ring4_coords, 'ED1')

if __name__ == "__main__":main()


