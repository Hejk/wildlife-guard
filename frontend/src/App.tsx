import { useEffect, useMemo, useState } from 'react'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { Badge, Layout, Menu, Space, Typography } from 'antd'
import {
  DashboardOutlined,
  DesktopOutlined,
  FileTextOutlined,
  NotificationOutlined,
  SettingOutlined,
  SoundOutlined,
} from '@ant-design/icons'

import Dashboard from '@/pages/Dashboard'
import AudioManager from '@/pages/AudioManager'
import Logs from '@/pages/Logs'
import DeviceConfigPage from '@/pages/Config'
import DeviceStatus from '@/pages/DeviceStatus'
import { useDeviceStore } from '@/stores/deviceStore'

const { Header, Sider, Content } = Layout
const { Title } = Typography

export default function App() {
  const navigate = useNavigate()
  const location = useLocation()
  const { connected, fetchStatus } = useDeviceStore()
  const [collapsed, setCollapsed] = useState(false)

  useEffect(() => {
    fetchStatus()
  }, [fetchStatus])

  const menuItems = useMemo(
    () => [
      { key: '/', icon: <DashboardOutlined />, label: '数据看板' },
      { key: '/audio', icon: <SoundOutlined />, label: '音频管理' },
      { key: '/logs', icon: <FileTextOutlined />, label: '日志查看' },
      { key: '/config', icon: <SettingOutlined />, label: '设备配置' },
      { key: '/device', icon: <DesktopOutlined />, label: '设备状态' },
    ],
    [],
  )

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed} theme="dark">
        <div
          style={{
            height: 56,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            color: '#fff',
            fontWeight: 600,
            whiteSpace: 'nowrap',
          }}
        >
          <NotificationOutlined />
          {!collapsed && <span>智哨 Smart Sentinel</span>}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: '#fff',
            padding: '0 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Title level={4} style={{ margin: 0 }}>
            基于端云协同的农田生态防御系统管理后台
          </Title>
          <Space>
            <Badge status={connected ? 'success' : 'default'} />
            <span>{connected ? '设备已连接' : '设备未连接'}</span>
          </Space>
        </Header>
        <Content style={{ margin: 16 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/audio" element={<AudioManager />} />
            <Route path="/logs" element={<Logs />} />
            <Route path="/config" element={<DeviceConfigPage />} />
            <Route path="/device" element={<DeviceStatus />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}
