// frontend/src/utils/formatDate.js
export function formatChromeStyle(isoString) {
  const date = new Date(isoString)
  const now = new Date()

  const isToday = date.toDateString() === now.toDateString()

  const yesterday = new Date(now)
  yesterday.setDate(now.getDate() - 1)
  const isYesterday = date.toDateString() === yesterday.toDateString()

  const hh = String(date.getHours()).padStart(2, '0')
  const mm = String(date.getMinutes()).padStart(2, '0')

  if (isToday) {
    return `今天 ${hh}:${mm}`
  }
  if (isYesterday) {
    return `昨天 ${hh}:${mm}`
  }

  const isSameYear = date.getFullYear() === now.getFullYear()
  if (isSameYear) {
    return `${date.getMonth() + 1}月${date.getDate()}日`
  }
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
}