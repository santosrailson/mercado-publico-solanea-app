import { useEffect, useRef } from 'react'
import { useAuthStore } from '@/store/auth'

const INACTIVITY_TIMEOUT_MINUTES = 30

export function useInactivityLogout() {
  const logout = useAuthStore((state) => state.logout)
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (!isAuthenticated) {
      if (timerRef.current) {
        clearTimeout(timerRef.current)
        timerRef.current = null
      }
      return
    }

    const handleInactivity = () => {
      logout()
      window.location.href = '/login'
    }

    const resetTimer = () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current)
      }
      timerRef.current = setTimeout(
        handleInactivity,
        INACTIVITY_TIMEOUT_MINUTES * 60 * 1000
      )
    }

    const events = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart']

    events.forEach((event) => {
      window.addEventListener(event, resetTimer, { passive: true })
    })

    resetTimer()

    return () => {
      events.forEach((event) => {
        window.removeEventListener(event, resetTimer)
      })
      if (timerRef.current) {
        clearTimeout(timerRef.current)
      }
    }
  }, [isAuthenticated, logout])
}
