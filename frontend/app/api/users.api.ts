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
}

export interface GameResponse {
  id: number
  name: string
  image_url: string | null
  steam_app_id: string | null
  state: string
  is_favorite: boolean
}

export interface FetchSteamResponse {
  name: string
  image_url: string | null
  steam_app_id: string
}

export interface CreateGamePayload {
  name: string
  image_url?: string | null
  steam_app_id?: string | null
  state: string
  is_favorite?: boolean
}

export async function fetchMe(api: ApiClient) {
  return api<MeResponse>(ApiEndpoint.Users.ME)
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
