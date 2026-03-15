import type { ApiClient } from './base.client'
import { ApiEndpoint } from '~/constants/api'

export interface GameDetailResponse {
  id: number
  name: string
  image_url: string | null
  steam_app_id: string | null
  state: string
  is_favorite: boolean
  genres: { id: string; description: string }[] | null
  developers: string[] | null
  publishers: string[] | null
  release_date: string | null
  note: string | null
  date_started: string | null
  date_finished: string | null
  hours_played: number | null
  view_count: number
  owner: {
    username: string | null
    tag: string | null
    avatar_url: string | null
  }
}

export async function fetchGame(api: ApiClient, id: number) {
  return api<GameDetailResponse>(ApiEndpoint.Games.BY_ID(id))
}
