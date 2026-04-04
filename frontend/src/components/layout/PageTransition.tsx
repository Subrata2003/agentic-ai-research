import { motion, AnimatePresence } from 'framer-motion'
import { useLocation } from 'react-router-dom'
import type { ReactNode } from 'react'

interface PageTransitionProps {
  children: ReactNode
}

/**
 * Wraps page content with a Framer Motion fade+slide transition.
 * Used inside AppShell around the <Outlet />.
 *
 * Forward navigation: slide in from right (x: 16 → 0)
 * All transitions: 200ms ease-out — fast enough to not feel sluggish
 */
export default function PageTransition({ children }: PageTransitionProps) {
  const { pathname } = useLocation()

  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={pathname}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{    opacity: 0, y: -4 }}
        transition={{ duration: 0.18, ease: 'easeOut' }}
        className="h-full"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
