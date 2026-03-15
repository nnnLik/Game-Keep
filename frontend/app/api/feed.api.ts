import type { ApiClient } from './base.client'
import type { CommentResponse } from './games.api'
import { ApiEndpoint } from '~/constants/api'

export type FeedActionType = 'game_created' | 'favorite_added' | 'favorite_removed'

export interface FeedPostAuthor {
  username: string | null
  tag: string | null
  avatar_url: string | null
}

export interface FeedPostGame {
  id: number
  name: string
  image_url: string | null
  state: string
}

export interface FeedPost {
  id: number
  action_type: FeedActionType
  created_at: string
  author: FeedPostAuthor
  game: FeedPostGame
  like_count: number
  dislike_count: number
  current_user_voted: { liked: boolean; disliked: boolean }
  comments?: CommentResponse[] | null
  comments_total?: number | null
}

export interface FeedResponse {
  items: FeedPost[]
  next_cursor: number | null
  has_more: boolean
}

export async function fetchFeed(
  api: ApiClient,
  params?: { cursor?: number | null; limit?: number }
) {
  const searchParams = new URLSearchParams()
  if (params?.cursor != null) searchParams.set('cursor', String(params.cursor))
  if (params?.limit != null) searchParams.set('limit', String(params.limit))
  const query = searchParams.toString()
  const url = query ? `${ApiEndpoint.Feed.LIST}?${query}` : ApiEndpoint.Feed.LIST
  return api<FeedResponse>(url)
}

export async function fetchActivity(
  api: ApiClient,
  tag: string,
  params?: { cursor?: number | null; limit?: number }
) {
  const searchParams = new URLSearchParams()
  if (params?.cursor != null) searchParams.set('cursor', String(params.cursor))
  if (params?.limit != null) searchParams.set('limit', String(params.limit))
  const query = searchParams.toString()
  const url = query
    ? `${ApiEndpoint.Feed.ACTIVITY(tag)}?${query}`
    : ApiEndpoint.Feed.ACTIVITY(tag)
  return api<FeedResponse>(url)
}

export async function voteActivity(
  api: ApiClient,
  activityId: number,
  isLike: boolean
) {
  return api(ApiEndpoint.Feed.VOTE(activityId), {
    method: 'POST',
    body: { is_like: isLike },
  })
}
