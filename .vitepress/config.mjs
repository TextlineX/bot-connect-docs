import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Bot Connect',
  description: '机器人控制与通信平台文档',
  lang: 'zh-CN',
  ignoreDeadLinks: true,

  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    ['meta', { name: 'theme-color', content: '#3eaf7c' }],
  ],

  themeConfig: {
    siteTitle: 'Bot Connect',

    nav: [
      { text: '首页', link: '/' },
      { text: '项目文档', link: '/project/overview' },
      { text: '环境搭建', link: '/setup/setup' },
      { text: '官方文档', link: '/official/sdk' },
    ],

    sidebar: {
      '/project/': [
        {
          text: '项目文档',
          items: [
            { text: '总览与架构', link: '/project/overview' },
            { text: 'PC端部署', link: '/project/pc-deploy' },
            { text: '机器人端部署', link: '/project/robot-deploy' },
            { text: '真机启动手册', link: '/project/startup' },
            { text: '同步与运行指南', link: '/project/sync' },
            { text: '监控面板说明', link: '/project/monitor' },
            { text: '动作测试与映射', link: '/project/actions' },
            { text: 'Master模块能力清单', link: '/project/modules' },
            { text: '目录与排查速查', link: '/project/troubleshooting' },
          ],
        },
      ],
      '/setup/': [
        {
          text: '环境搭建',
          items: [
            { text: '环境安装', link: '/setup/setup' },
            { text: '容器环境修复', link: '/setup/container' },
            { text: '远程调试与同步', link: '/setup/remote-debug' },
          ],
        },
      ],
      '/sensors/': [
        {
          text: '传感器硬件抽象层',
          items: [
            { text: '常用话题速查', link: '/sensors/topic-cheatsheet' },
            { text: '3D激光雷达', link: '/sensors/lidar' },
            { text: '关节执行器', link: '/sensors/joints' },
            { text: '左目视觉相机', link: '/sensors/camera-left' },
            { text: '电池BMS', link: '/sensors/battery' },
            { text: '电源管理单元', link: '/sensors/pmu' },
            { text: '语音音频', link: '/sensors/audio' },
            { text: '运动控制', link: '/sensors/motion' },
            { text: '胸部惯导', link: '/sensors/imu-chest' },
            { text: '躯干惯导', link: '/sensors/imu-torso' },
            { text: '传感器数据监控', link: '/sensors/sensor-monitor' },
            { text: '系统监控诊断', link: '/sensors/diagnostics' },
          ],
        },
      ],
      '/development/': [
        {
          text: '开发规范',
          items: [
            { text: '二次开发指南', link: '/development/guide' },
            { text: '传感器编程规范', link: '/development/sensor-code' },
          ],
        },
      ],
      '/slam/': [
        {
          text: 'SLAM算法',
          items: [
            { text: 'FAST-LIO算法对接', link: '/slam/fast-lio' },
            { text: '雷达点云解码优化', link: '/slam/lidar-optimization' },
          ],
        },
      ],
      '/official/': [
        {
          text: '机器人基础',
          items: [
            { text: 'SDK 概览', link: '/official/sdk' },
            { text: '坐标系统', link: '/official/sdk/coordinate_system' },
            { text: '关节名称与限制', link: '/official/sdk/joint_name_and_limit' },
            { text: '部件名称', link: '/official/sdk/part_name' },
            { text: '机器人规格', link: '/official/sdk/robot_specifications' },
            { text: '传感器视野', link: '/official/sdk/sensor_fov' },
            { text: '板载计算机', link: '/official/sdk/onboard_computer' },
            { text: '用户调试接口', link: '/official/sdk/user_debug_interface' },
          ],
        },
        {
          text: '操作指南',
          items: [
            { text: '开机指南', link: '/official/2_operation_guide/start_up_guide' },
            { text: '机器人连接', link: '/official/2_operation_guide/robot_connection' },
            { text: '遥控器', link: '/official/2_operation_guide/remote_controller' },
            { text: '关机', link: '/official/2_operation_guide/shutdown' },
          ],
        },
        {
          text: 'SDK 开发',
          items: [
            { text: '快速开始', link: '/official/quickstart' },
            { text: '代码示例(Python)', link: '/official/examples/python' },
            { text: '代码示例(C++)', link: '/official/examples/cpp' },
          ],
        },
        {
          text: '接口文档',
          items: [
            { text: 'FASM', link: '/official/interface/FASM' },
            { text: '运动控制', link: '/official/interface/control_mod' },
            { text: 'HAL 硬件抽象层', link: '/official/interface/hal' },
            { text: '交互器', link: '/official/interface/interactor' },
            { text: '感知', link: '/official/interface/perception' },
          ],
        },
        {
          text: '其他',
          items: [
            { text: 'FAQ', link: '/official/faq' },
            { text: '更新日志', link: '/official/changelog' },
            { text: '反馈', link: '/official/feedback' },
          ],
        },
      ],
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/TextlineX/bot-connect-docs' },
    ],

    search: {
      provider: 'local',
      options: { detailedView: true },
    },

    editLink: {
      pattern: 'https://github.com/TextlineX/bot-connect-docs/edit/main/docs/:path',
      text: '在 GitHub 上编辑此页',
    },

    footer: {
      message: '基于 AGIBOT X2 平台构建',
      copyright: 'MIT License',
    },
  },

  vue: {
    template: {
      transformAssetUrls: false,
    },
  },
  markdown: {
    lineNumbers: true,
    config(md) {
      md.set({ html: false })
    },
  },
  cleanUrls: true,
})
