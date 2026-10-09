import ReactECharts from 'echarts-for-react'

// 采用宽松的 echarts option 结构，避免各页面与 echarts 联合类型的无谓摩擦
interface Props {
  option: Record<string, unknown>
  height?: number
}

export default function EChart({ option, height = 320 }: Props) {
  return (
    <ReactECharts
      option={option}
      style={{ height, width: '100%' }}
      notMerge
      lazyUpdate
    />
  )
}
