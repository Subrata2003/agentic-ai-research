import { create } from 'zustand'

interface CompareState {
  leftId: string | null
  rightId: string | null
  setLeft: (id: string | null) => void
  setRight: (id: string | null) => void
  swap: () => void
  clear: () => void
}

export const useCompareStore = create<CompareState>()((set) => ({
  leftId: null,
  rightId: null,

  setLeft: (id) => set({ leftId: id }),
  setRight: (id) => set({ rightId: id }),

  swap: () =>
    set((s) => ({ leftId: s.rightId, rightId: s.leftId })),

  clear: () => set({ leftId: null, rightId: null }),
}))
