import numpy as np
from physics_sim import PhysicsSim

class TaskGo():
    """Task (environment) that defines the goal and provides feedback to the agent."""
    def __init__(self, init_pose=None, init_velocities=None, 
        init_angle_velocities=None, runtime=5., target_pos=None):
        """Initialize a Task object.
        Params
        ======
            init_pose: initial position of the quadcopter in (x,y,z) dimensions and the Euler angles
            init_velocities: initial velocity of the quadcopter in (x,y,z) dimensions
            init_angle_velocities: initial radians/second for each of the three Euler angles
            runtime: time limit for each episode
            target_pos: target/goal (x,y,z) position for the agent
        """
        # Simulation
        self.sim = PhysicsSim(init_pose, init_velocities, init_angle_velocities, runtime) 
        self.action_repeat = 3

        self.state_size = self.action_repeat * 6
        # self.state_size = self.action_repeat * 6 + 3
        self.action_low = 0
        # self.action_low = 50
        self.action_high = 900
        # self.action_high = 500
        self.action_size = 4

        # Goal
        self.target_pos = target_pos if target_pos is not None else np.array([0., 0., 10.]) 

        

    def get_reward(self):
        """Uses current pose of sim to return reward."""
        # reward = 1.-.3*(abs(self.sim.pose[:3] - self.target_pos)).sum()

        # Reward positive velocity along z-axis
        # reward = 0.0
        reward = self.sim.v[2]
        # Reward positions close to target along z-axis
        reward -= (abs(self.sim.pose[2] - self.target_pos[2])) / 2.0 
        # A lower sensativity towards drifting in the xy-plane
        reward -= (abs(self.sim.pose[:2] - self.target_pos[:2])).sum() / 4.0
        reward -= (abs(self.sim.angular_v[:3])).sum()


        return reward
        
        # reward = -abs(self.sim.pose[2] - self.target_pos[2])
        # if abs(self.sim.pose[2] - self.target_pos[2]) < 1:  # agent has crossed the target height
        #     reward += 10.0  # bonus reward
        # return reward


    def step(self, rotor_speeds):
        """Uses action to obtain next state, reward, done."""
        reward = 0
        pose_all = []
        for _ in range(self.action_repeat):
            done = self.sim.next_timestep(rotor_speeds) # update the sim pose and velocities
            reward += self.get_reward() 
            pose_all.append(self.sim.pose)

            if(self.sim.pose[2] >= self.target_pos[2]):
                reward += 100
                done = True
        # add target
        # pose_all.append(self.target_pos)
        next_state = np.concatenate(pose_all)

        return next_state, reward, done

    def reset(self):
        """Reset the sim to start a new episode."""
        self.sim.reset()
        # print('sim pos: ')
        # print(self.sim.pose)
        state = np.concatenate([self.sim.pose] * self.action_repeat)
        # state = np.concatenate((state, self.target_pos))
        # print('state: ')
        # print(state)
        return state
