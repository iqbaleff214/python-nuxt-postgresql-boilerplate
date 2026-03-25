export const useSidebar = () => {
  const collapsed = useCookie<boolean>('sidebar-collapsed', { default: () => false })
  const mobileOpen = useState('sidebar-mobile-open', () => false)

  return {
    collapsed,
    mobileOpen,
    toggle: () => { collapsed.value = !collapsed.value },
    openMobile: () => { mobileOpen.value = true },
    closeMobile: () => { mobileOpen.value = false },
    toggleMobile: () => { mobileOpen.value = !mobileOpen.value },
  }
}
