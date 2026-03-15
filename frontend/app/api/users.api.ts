import type { ApiClient } from './base.client'
import { ApiEndpoint } from '~/constants'

export interface MeResponse {
  id: string
  username: string | null
  tag: string | null
  email: string
  created_at: string
  is_registration_complete: boolean
  avatar_url: string | null
  banner_url: string | null
}

export interface GenreItem {
  id: string
  description: string
}

export interface GameResponse {
  id: number
  name: string
  image_url: string | null
  steam_app_id: string | null
  state: string
  is_favorite: boolean
  genres: GenreItem[] | null
  developers: string[] | null
  publishers: string[] | null
  release_date: string | null
  note: string | null
  date_started: string | null
  date_finished: string | null
  hours_played: number | null
}

export interface FetchSteamResponse {
  name: string
  image_url: string | null
  steam_app_id: string
  genres: GenreItem[]
  developers: string[]
  publishers: string[]
  release_date: string | null
}

export interface CreateGamePayload {
  name: string
  image_url?: string | null
  steam_app_id?: string | null
  state: string
  is_favorite?: boolean
  genres?: GenreItem[] | null
  developers?: string[] | null
  publishers?: string[] | null
  release_date?: string | null
  note?: string | null
  date_started?: string | null
  date_finished?: string | null
  hours_played?: number | null
}

export interface ProfileByTagResponse {
  username: string | null
  tag: string | null
  avatar_url: string | null
  banner_url: string | null
  created_at: string | null
  games: GameResponse[]
}

export async function fetchMe(api: ApiClient) {
  return api<MeResponse>(ApiEndpoint.Users.ME)
}

export async function fetchProfileByTag(api: ApiClient, tag: string) {
  return api<ProfileByTagResponse>(ApiEndpoint.Users.BY_TAG(tag))
}

export async function fetchMyGames(
  api: ApiClient,
  params?: { state?: string; is_favorite?: boolean }
) {
  const searchParams = new URLSearchParams()
  if (params?.state) searchParams.set('state', params.state)
  if (params?.is_favorite !== undefined)
    searchParams.set('is_favorite', String(params.is_favorite))
  const query = searchParams.toString()
  const url = query ? `${ApiEndpoint.Users.ME_GAMES}?${query}` : ApiEndpoint.Users.ME_GAMES
  return api<GameResponse[]>(url)
}

export async function fetchSteamGame(api: ApiClient, steamUrl: string) {
  return api<FetchSteamResponse>(ApiEndpoint.Users.ME_GAMES_FETCH_STEAM, {
    method: 'POST',
    body: { steam_url: steamUrl },
  })
}

export async function createGame(api: ApiClient, payload: CreateGamePayload) {
  return api<GameResponse>(ApiEndpoint.Users.ME_GAMES, {
    method: 'POST',
    body: payload,
  })
}

export async function uploadBanner(api: ApiClient, file: Blob) {
  const formData = new FormData()
  formData.append('banner', file, 'banner.png')
  return api<MeResponse>(ApiEndpoint.Users.ME_BANNER, {
    method: 'PATCH',
    body: formData,
  })
}

export async function deleteBanner(api: ApiClient) {
  return api<MeResponse>(ApiEndpoint.Users.ME_BANNER, {
    method: 'DELETE',
  })
}
