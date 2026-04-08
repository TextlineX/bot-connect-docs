from setuptools import setup, find_packages

package_name = 'x2_bot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'rclpy', 'aimdk_msgs'],
    zip_safe=True,
    maintainer='x2',
    maintainer_email='todo@todo.com',
    description='Custom skills for master/slave (audio, tts, actions).',
    license='MIT',
    entry_points={
        'console_scripts': [
            'tts_client = x2_bot.tts_client_node:main',
            'mic_sub = x2_bot.mic_sub_node:main',
        ],
    },
)
