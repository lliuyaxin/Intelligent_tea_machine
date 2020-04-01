#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Author: Liuyaxin <17865196312@163.com>

from pykinect2 import PyKinectV2
from pykinect2 import PyKinectRuntime
from threading import Thread
import pygame
import ctypes
import math
import time
import queue

class BodyGameRuntime(object):
    def __init__(self):
        pygame.init()

        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()

        # Set the width and height of the screen [width, height]
        self._infoObject = pygame.display.Info()
        self._screen = pygame.display.set_mode((self._infoObject.current_w >> 1, self._infoObject.current_h >> 1),
                                               pygame.HWSURFACE |pygame.DOUBLEBUF|pygame.RESIZABLE, 32)

        pygame.display.set_caption("Kinect for Windows v2 Body Game")

        # Loop until the user clicks the close button.
        self._done = False

        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()

        # Kinect runtime object, we want only color and body frames
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)

        # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)

        # here we will store skeleton data
        self._bodies = None

    def draw_body_bone(self, joints, jointPoints, color, joint0, joint1):
        joint0State = joints[joint0].TrackingState;
        joint1State = joints[joint1].TrackingState;

        # both joints are not tracked
        if (joint0State == PyKinectV2.TrackingState_NotTracked) or (joint1State == PyKinectV2.TrackingState_NotTracked):
            return

        # both joints are not *really* tracked
        if (joint0State == PyKinectV2.TrackingState_Inferred) and (joint1State == PyKinectV2.TrackingState_Inferred):
            return

        # ok, at least one is good
        start = (jointPoints[joint0].x, jointPoints[joint0].y)
        end = (jointPoints[joint1].x, jointPoints[joint1].y)

        try:
            pygame.draw.line(self._frame_surface, color, start, end, 8)
            # pygame.draw.circle(self._frame_surface,(255,0,0),start,100)
            # pygame.draw.circle(self._frame_surface,(255,0,0),end,100)
        except: # need to catch it due to possible invalid positions (with inf)
            pass

    def draw_body(self, joints, jointPoints, color):
        # Torso
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder,
                            PyKinectV2.JointType_SpineMid);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder,
                            PyKinectV2.JointType_ShoulderRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder,
                            PyKinectV2.JointType_ShoulderLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft);

        # Right Arm
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderRight,
                            PyKinectV2.JointType_ElbowRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowRight,
                            PyKinectV2.JointType_WristRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight,
                            PyKinectV2.JointType_HandRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandRight,
                            PyKinectV2.JointType_HandTipRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight,
                            PyKinectV2.JointType_ThumbRight);

        # Left Arm
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderLeft,
                            PyKinectV2.JointType_ElbowLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_HandLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandLeft,
                            PyKinectV2.JointType_HandTipLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_ThumbLeft);

        # Right Leg
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeRight,
                            PyKinectV2.JointType_AnkleRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleRight,
                            PyKinectV2.JointType_FootRight);

        # Left Leg
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleLeft, PyKinectV2.JointType_FootLeft);

    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        address = self._kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()

    def get_name(self,n):
        if n == 0:
            return "SpineBase"
        elif n == 1:
            return "SpineMid"
        elif n == 4:
            return "ShoulderLeft"
        elif n == 5:
            return "ElbowLeft"
        elif n == 6:
            return "WristLeft"
        elif n == 7:
            return "HandLeft"
        elif n == 8:
            return "ShoulderRight"
        elif n == 9:
            return "ElbowRight"
        elif n == 10:
            return "WristRight"
        elif n == 11:
            return "HandRight"
        elif n == 20:
            return "SpineShoulder"
        else:
            return "NULL"


    def get_angle(self,joints,joint0,joint1,joint2):

        JointA=[joints[joint1].Position.x-joints[joint0].Position.x,joints[joint1].Position.y-joints[joint0].Position.y,joints[joint1].Position.z-joints[joint0].Position.z]
        JointB=[joints[joint1].Position.x-joints[joint2].Position.x,joints[joint1].Position.y-joints[joint2].Position.y,joints[joint1].Position.z-joints[joint2].Position.z]

        JointC=math.pow(JointA[0],2)+math.pow(JointA[1],2)+math.pow(JointA[2],2)
        JointAL=math.pow(JointC,0.5)
        JointD=math.pow(JointB[0],2)+math.pow(JointB[1],2)+math.pow(JointB[2],2)
        JointBL = math.pow(JointD, 0.5)

        dotProduct=JointA[0] * JointB[0] + JointA[1] * JointB[1] + JointA[2] * JointB[2]
        cosr=dotProduct / JointAL / JointBL
        angle=math.acos(cosr)*180/math.pi

        return angle

    def get_angle2(self, joints, joint0, joint1, joint2,joint3):
        JointA = [joints[joint1].Position.x - joints[joint0].Position.x, joints[joint1].Position.y - joints[joint0].Position.y,joints[joint1].Position.z - joints[joint0].Position.z]
        JointB = [joints[joint3].Position.x - joints[joint2].Position.x, joints[joint3].Position.y - joints[joint2].Position.y,joints[joint3].Position.z - joints[joint2].Position.z]

        JointC = math.pow(JointA[0], 2) + math.pow(JointA[1], 2) + math.pow(JointA[2], 2)
        JointAL = math.pow(JointC, 0.5)
        JointD = math.pow(JointB[0], 2) + math.pow(JointB[1], 2) + math.pow(JointB[2], 2)
        JointBL = math.pow(JointD, 0.5)

        dotProduct = JointA[0] * JointB[0] + JointA[1] * JointB[1] + JointA[2] * JointB[2]
        cosr = dotProduct / JointAL / JointBL
        angle = math.acos(cosr) * 180 / math.pi

        return angle

    def get_all_angle(self,joints,angle_array):

        angle_array.append( self.get_angle2(joints,PyKinectV2.JointType_HipRight,PyKinectV2.JointType_HipLeft,PyKinectV2.JointType_ElbowLeft,PyKinectV2.JointType_ShoulderLeft) )
        angle_array.append( self.get_angle2(joints, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid,PyKinectV2.JointType_ShoulderLeft,PyKinectV2.JointType_ElbowLeft) )
        angle_array.append( self.get_angle(joints, PyKinectV2.JointType_ShoulderLeft, PyKinectV2.JointType_ElbowLeft,PyKinectV2.JointType_WristLeft) )
        angle_array.append( 0 )
        angle_array.append( self.get_angle(joints, PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft,PyKinectV2.JointType_HandLeft) )

        angle_array.append( self.get_angle2(joints,PyKinectV2.JointType_HipRight,PyKinectV2.JointType_HipLeft,PyKinectV2.JointType_ShoulderRight,PyKinectV2.JointType_ElbowRight) )
        angle_array.append( self.get_angle2(joints, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid,PyKinectV2.JointType_ShoulderRight,PyKinectV2.JointType_ElbowRight) )
        angle_array.append( self.get_angle(joints, PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight,PyKinectV2.JointType_WristRight) )
        angle_array.append ( 0 )
        angle_array.append( self.get_angle(joints, PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight,PyKinectV2.JointType_HandRight) )

        return angle_array

    def get_data(self,queue_left,queue_right,target_joint):
        # --- We have a body frame, so can get skeletons
        if self._kinect.has_new_body_frame():
            self._bodies = self._kinect.get_last_body_frame()

        target_joint_number = [0, 0, 0, 0, 0, 0]

        # --- Get the best detection target
        if self._bodies is not None:
            for i in range(0, self._kinect.max_body_count):
                body = self._bodies.bodies[i]
                if body.is_tracked:
                    joints = body.joints
                    for j in range(0, 25):
                        for z in range(0, 11):
                            if ((j == target_joint[z]) and (joints[j].TrackingState == PyKinectV2.TrackingState_Tracked)):
                                target_joint_number[i] = target_joint_number[i] + 1

            print(time.clock())
            print(target_joint_number)

            max_target_joint_number = 0
            for k in range(0, self._kinect.max_body_count):
                if (target_joint_number[k] > max_target_joint_number):
                    max_target_joint_number = k

            target_joint_number.clear()

            body = self._bodies.bodies[max_target_joint_number]
            if body.is_tracked:

                # left_hand_state = PyKinectV2.HandState_Unknown
                # right_hand_state = PyKinectV2.HandState_Unknown

                # --- get handstate data
                # left_hand_state = body.hand_left_state
                # right_hand_state = body.hand_right_state
                # print(left_hand_state, right_hand_state)

                """
                angle_array[0]：左臂肩关节内外运动
                angle_array[1]：左臂肩关节前后运动
                angle_array[2]：左臂肘关节屈伸运动
                angle_array[3]：左臂腕关节掌曲背伸运动,输出固定值0
                angle_array[4]：左臂腕关节内外旋运动
                angle_array[5]：右臂肩关节内外运动
                angle_array[6]：右臂肩关节前后运动
                angle_array[7]：右臂肘关节屈伸运动
                angle_array[8]：右臂腕关节掌曲背伸运动,输出固定值0
                angle_array[9]：右臂腕关节内外旋运动
                """
                # --- get joint angle data
                angle_left = []
                angle_right = []
                joints = body.joints
                # --- get all joint angle data
                self.get_left_angle(joints, angle_left)
                self.get_right_angle(joints, angle_right)
                # print(angle_array)
                if (joints[PyKinectV2.JointType_ShoulderLeft].Position.y > joints[PyKinectV2.JointType_WristLeft].Position.y):
                    angle_left[2] = -angle_left[2]
                if (joints[PyKinectV2.JointType_ShoulderRight].Position.y > joints[PyKinectV2.JointType_WristRight].Position.y):
                    angle_right[2] = -angle_right[2]
                print("kinect输出左臂（入队列）:", angle_left)
                print("kinect输出右臂（入队列）", angle_right)
                queue_left.put(angle_left)
                queue_right.put(angle_right)
                # --- convert joint coordinates from depth space to color space
                joint_points = self._kinect.body_joints_to_color_space(joints)
                self.draw_body(joints, joint_points, (0, 255, 0))

    def run(self,type):

        q = queue.Queue(1800)
        frame_number = 0
        # -------- Main Program Loop -----------
        while not self._done:
            # --- Main event loop
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    self._done = True  # Flag that we are done so we exit this loop

                elif event.type == pygame.VIDEORESIZE:  # window resized
                    self._screen = pygame.display.set_mode(event.dict['size'],
                                                           pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE, 32)

            if self._kinect.has_new_color_frame():
                frame = self._kinect.get_last_color_frame()
                self.draw_color_frame(frame, self._frame_surface)
                frame = None
            target_joint = (0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 20)
            t = []
            self.get_body_frame(q, target_joint)
            # print(q.empty())
            if not q.empty():
                angle = q.get()

                left_move = Thread(target=type.move_arm_left, args=(angle[0], angle[1], angle[2], angle[3], angle[4]))
                t.append(left_move)
                right_move = Thread(target=type.move_arm_right, args=(angle[5], angle[6], angle[7], angle[8], angle[9]))
                t.append(right_move)

            for x in t:
                x.start()
            for x in t:
                x.join()

            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size)
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));
            self._screen.blit(surface_to_draw, (0, 0))
            surface_to_draw = None
            pygame.display.update()

            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # --- Limit to 30 frames per second
            self._clock.tick(30)
            # time.sleep(1)

        # Close our Kinect sensor, close the window and quit.
        self._kinect.close()
        pygame.quit()