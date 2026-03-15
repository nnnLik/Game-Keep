const avatarVersion = ref(0)

export function useAvatarChange() {
  return {
    /** Вызвать после успешного изменения аватара — подписчики обновят данные */
    emitAvatarChange: () => {
      avatarVersion.value++
    },
    /** Реактивная версия — при изменении нужно перезапросить /users/me */
    avatarVersion: readonly(avatarVersion),
  }
}
