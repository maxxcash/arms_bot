import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node


def generate_launch_description():

    package_name = 'arms_bot'

    # Robot State Publisher
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory(package_name), 'launch', 'rsp.launch.py')
        ]),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        ])
    )

    # Spawn robot in Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'my_bot'],
        output='screen'
    )

    # Spawner: Joint state broadcaster (this must be spawned first, without delay)
    joint_broad_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen'
    )

    # Spawner: Diff drive controller (delayed)
    diff_drive_spawner = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['differential_drive_controller'],
                output='screen'
            )
        ]
    )

    # Spawner: Linear actuator controller (delayed)
    # line_cont_spawner = TimerAction(
    #     period=5.0,
    #     actions=[
    #         Node(
    #             package='controller_manager',
    #             executable='spawner',
    #             arguments=['linear_actuator_controller'],
    #             output='screen'
    #         )
    #     ]
    # )

    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        joint_broad_spawner,  # No delay — joint states should always be first
        diff_drive_spawner,
        # line_cont_spawner
    ])
