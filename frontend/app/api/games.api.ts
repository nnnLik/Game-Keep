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

export interface CommentAuthor {
  username: string | null
  tag: string | null
  avatar_url: string | null
}

export interface CommentResponse {
  id: number
  text: string
  created_at: string
  author: CommentAuthor
  like_count: number
  dislike_count: number
  current_user_voted: { liked: boolean; disliked: boolean }
  children: CommentResponse[]
}

export async function fetchGame(api: ApiClient, id: number) {
  return api<GameDetailResponse>(ApiEndpoint.Games.BY_ID(id))
}

export async function fetchComments(api: ApiClient, gameId: number) {
  return api<CommentResponse[]>(ApiEndpoint.Games.COMMENTS(gameId))
}

export async function createComment(
  api: ApiClient,
  gameId: number,
  text: string,
  parentId?: number | null
) {
  return api<{ id: number }>(ApiEndpoint.Games.COMMENTS(gameId), {
    method: 'POST',
    body: { text, parent_id: parentId ?? null },
  })
}

export async function voteComment(
  api: ApiClient,
  gameId: number,
  commentId: number,
  isLike: boolean
) {
  return api<{ ok: boolean }>(ApiEndpoint.Games.COMMENT_VOTE(gameId, commentId), {
    method: 'POST',
    body: { is_like: isLike },
  })
}
