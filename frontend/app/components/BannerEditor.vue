<script setup lang="ts">
const props = defineProps<{
  modelValue: boolean
  initialImageUrl?: string | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  created: [blob: Blob]
}>()

const CANVAS_WIDTH = 1200
const CANVAS_HEIGHT = 400

const canvasEl = ref<HTMLCanvasElement | null>(null)

const tool = ref<'pencil' | 'eraser' | 'bucket' | 'line' | 'rect' | 'circle'>('pencil')
const brushSize = ref(4)
const color = ref('#000000')
const submitting = ref(false)

const BRUSH_SIZES = [2, 4, 6, 10]
const PALETTE = [
  '#000000',
  '#ffffff',
  '#ef4444',
  '#f97316',
  '#eab308',
  '#22c55e',
  '#3b82f6',
  '#8b5cf6',
  '#ec4899',
  '#06b6d4',
  '#6b7280',
  '#374151',
]

const history: string[] = []
let historyIndex = -1

function ctx() {
  return canvasEl.value?.getContext('2d')
}

function saveState() {
  if (!canvasEl.value) return
  const data = canvasEl.value.toDataURL('image/png')
  if (historyIndex < history.length - 1) history.splice(historyIndex + 1)
  history.push(data)
  if (history.length > 50) history.shift()
  historyIndex = history.length - 1
}

function restoreState() {
  if (!canvasEl.value || historyIndex < 0) return
  const src = history[historyIndex]
  if (!src) return
  const img = new Image()
  img.onload = () => {
    const c = ctx()
    if (!c) return
    c.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
    c.drawImage(img, 0, 0)
  }
  img.src = src
}

function undo() {
  if (historyIndex <= 0) return
  historyIndex--
  restoreState()
}

function redo() {
  if (historyIndex >= history.length - 1) return
  historyIndex++
  restoreState()
}

function clearCanvas() {
  const c = ctx()
  if (!c) return
  c.fillStyle = '#ffffff'
  c.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
  history.length = 0
  historyIndex = -1
  saveState()
}

function setTool(t: typeof tool.value) {
  tool.value = t
}

function setColor(c: string) {
  color.value = c
}

function setBrushSize(s: number) {
  brushSize.value = s
}

function getPos(e: MouseEvent | TouchEvent): { x: number; y: number } {
  const rect = canvasEl.value?.getBoundingClientRect()
  if (!rect) return { x: 0, y: 0 }
  const clientX = 'touches' in e ? e.touches[0]?.clientX ?? e.changedTouches?.[0]?.clientX : e.clientX
  const clientY = 'touches' in e ? e.touches[0]?.clientY ?? e.changedTouches?.[0]?.clientY : e.clientY
  const scaleX = CANVAS_WIDTH / rect.width
  const scaleY = CANVAS_HEIGHT / rect.height
  return {
    x: ((clientX ?? 0) - rect.left) * scaleX,
    y: ((clientY ?? 0) - rect.top) * scaleY,
  }
}

let isDrawing = false
let startX = 0
let startY = 0

function floodFill(startX: number, startY: number, fillColor: string) {
  const c = ctx()
  if (!c || !canvasEl.value) return
  const w = CANVAS_WIDTH
  const h = CANVAS_HEIGHT
  const imgData = c.getImageData(0, 0, w, h)
  const data = imgData.data
  const startIdx = (Math.floor(startY) * w + Math.floor(startX)) * 4
  const r0 = data[startIdx] ?? 0
  const g0 = data[startIdx + 1] ?? 0
  const b0 = data[startIdx + 2] ?? 0
  const a0 = data[startIdx + 3] ?? 255
  const [fr, fg, fb] = hexToRgb(fillColor)
  if (r0 === fr && g0 === fg && b0 === fb) return
  const stack: [number, number][] = [[Math.floor(startX), Math.floor(startY)]]
  const visited = new Uint8Array(w * h)
  const idx = (x: number, y: number) => (y * w + x) * 4
  const tol = 8
  const same = (i: number) =>
    Math.abs((data[i] ?? 0) - r0) <= tol &&
    Math.abs((data[i + 1] ?? 0) - g0) <= tol &&
    Math.abs((data[i + 2] ?? 0) - b0) <= tol &&
    Math.abs((data[i + 3] ?? 255) - a0) <= tol
  while (stack.length) {
    const [x, y] = stack.pop()!
    if (x < 0 || x >= w || y < 0 || y >= h) continue
    const i = y * w + x
    if (visited[i]) continue
    const di = idx(x, y)
    if (!same(di)) continue
    visited[i] = 1
    data[di] = fr
    data[di + 1] = fg
    data[di + 2] = fb
    data[di + 3] = 255
    stack.push([x + 1, y], [x - 1, y], [x, y + 1], [x, y - 1])
  }
  c.putImageData(imgData, 0, 0)
}

function hexToRgb(hex: string): [number, number, number] {
  const m = hex.slice(1).match(/.{2}/g)
  if (!m || !m[0] || !m[1] || !m[2]) return [0, 0, 0]
  return [parseInt(m[0], 16), parseInt(m[1], 16), parseInt(m[2], 16)]
}

function onPointerDown(e: MouseEvent | TouchEvent) {
  if (!('touches' in e)) e.preventDefault()
  const { x, y } = getPos(e)
  startX = x
  startY = y
  if (tool.value === 'bucket') {
    saveState()
    floodFill(x, y, color.value)
    return
  }
  if (tool.value === 'pencil' || tool.value === 'eraser') {
    isDrawing = true
    const c = ctx()
    if (!c) return
    c.beginPath()
    c.moveTo(x, y)
    c.strokeStyle = tool.value === 'eraser' ? '#ffffff' : color.value
    c.lineWidth = tool.value === 'eraser' ? brushSize.value * 3 : brushSize.value
    c.lineCap = 'round'
    c.lineJoin = 'round'
  } else {
    isDrawing = true
  }
}

function onPointerMove(e: MouseEvent | TouchEvent) {
  if (!isDrawing || (tool.value !== 'pencil' && tool.value !== 'eraser')) return
  if (!('touches' in e)) e.preventDefault()
  const { x, y } = getPos(e)
  const c = ctx()
  if (!c) return
  c.lineTo(x, y)
  c.stroke()
}

function onPointerUp(e: MouseEvent | TouchEvent) {
  if (!isDrawing) return
  if (!('touches' in e)) e.preventDefault()
  const { x, y } = getPos(e)
  const c = ctx()
  if (tool.value === 'pencil' || tool.value === 'eraser') {
    isDrawing = false
    saveState()
    return
  }
  if (!c) return
  saveState()
  c.strokeStyle = color.value
  c.lineWidth = brushSize.value
  c.lineCap = 'round'
  if (tool.value === 'line') {
    c.beginPath()
    c.moveTo(startX, startY)
    c.lineTo(x, y)
    c.stroke()
  } else if (tool.value === 'rect') {
    c.strokeRect(
      Math.min(startX, x),
      Math.min(startY, y),
      Math.abs(x - startX),
      Math.abs(y - startY)
    )
  } else if (tool.value === 'circle') {
    const r = Math.hypot(x - startX, y - startY) / 2
    const cx = (startX + x) / 2
    const cy = (startY + y) / 2
    c.beginPath()
    c.arc(cx, cy, Math.max(r, 2), 0, Math.PI * 2)
    c.stroke()
  }
  isDrawing = false
}

function initCanvas() {
  const el = canvasEl.value
  if (!el) return
  el.width = CANVAS_WIDTH
  el.height = CANVAS_HEIGHT
  const c = el.getContext('2d')
  if (!c) return
  c.fillStyle = '#ffffff'
  c.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
  if (props.initialImageUrl) {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      c.drawImage(img, 0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
      saveState()
    }
    img.onerror = () => saveState()
    img.src = props.initialImageUrl
  } else {
    saveState()
  }
}

function close() {
  emit('update:modelValue', false)
}

function onEscape(e: KeyboardEvent) {
  if (e.key === 'Escape') close()
}

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      nextTick(() => {
        initCanvas()
      })
      window.addEventListener('keydown', onEscape)
    } else {
      window.removeEventListener('keydown', onEscape)
      history.length = 0
      historyIndex = -1
      tool.value = 'pencil'
    }
  }
)

onBeforeUnmount(() => window.removeEventListener('keydown', onEscape))

async function onSubmit() {
  if (!canvasEl.value) return
  submitting.value = true
  try {
    canvasEl.value.toBlob(
      (blob) => {
        if (blob) {
          emit('created', blob)
          close()
        }
        submitting.value = false
      },
      'image/png',
      1
    )
  } catch {
    submitting.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
      @click.self="close"
    >
      <div
        class="fixed inset-0 bg-black/60"
        aria-hidden="true"
        @click="close"
      />
      <div
        class="relative z-10 flex w-full max-w-6xl max-h-[95vh] flex-col overflow-hidden rounded-xl bg-gray-900 shadow-xl"
        role="dialog"
        aria-modal="true"
        aria-label="Редактор баннера"
        @click.stop
      >
        <!-- Верхняя панель: история, кисть, цвет, действия -->
        <div class="flex shrink-0 flex-wrap items-center gap-4 border-b border-gray-700 px-5 py-4">
          <div class="flex gap-1">
            <UTooltip text="Назад" :ui="{ content: '!z-[9999]' }">
              <UButton
                variant="soft"
                size="sm"
                icon="lucide:undo-2"
                aria-label="Назад"
                :disabled="historyIndex <= 0"
                @click="undo"
              />
            </UTooltip>
            <UTooltip text="Вперёд" :ui="{ content: '!z-[9999]' }">
              <UButton
                variant="soft"
                size="sm"
                icon="lucide:redo-2"
                aria-label="Вперёд"
                :disabled="historyIndex >= history.length - 1"
                @click="redo"
              />
            </UTooltip>
            <UTooltip text="Очистить" :ui="{ content: '!z-[9999]' }">
              <UButton
                variant="soft"
                size="sm"
                icon="lucide:trash-2"
                aria-label="Очистить"
                @click="clearCanvas"
              />
            </UTooltip>
          </div>
          <div class="h-5 w-px bg-gray-600" />
          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-400">Кисть</span>
            <button
              v-for="s in BRUSH_SIZES"
              :key="s"
              type="button"
              class="rounded border transition"
              :class="
                brushSize === s
                  ? 'border-emerald-500 bg-emerald-500/20'
                  : 'border-gray-600 hover:border-gray-500'
              "
              :style="{ width: s * 2 + 4 + 'px', height: s * 2 + 4 + 'px' }"
              @click="setBrushSize(s)"
            />
          </div>
          <div class="h-5 w-px bg-gray-600" />
          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-400">Цвет</span>
            <button
              v-for="c in PALETTE"
              :key="c"
              type="button"
              class="size-5 rounded-full border-2 transition shrink-0"
              :class="color === c ? 'border-white' : 'border-transparent'"
              :style="{ backgroundColor: c }"
              @click="setColor(c)"
            />
          </div>
          <div class="ml-auto flex gap-3">
            <UButton variant="soft" color="neutral" size="md" @click="close">
              Отмена
            </UButton>
            <UButton color="primary" size="md" :loading="submitting" @click="onSubmit">
              СОЗДАТЬ
            </UButton>
          </div>
        </div>

        <!-- Контент: слева инструменты, справа холст -->
        <div class="flex min-h-0 min-w-0 flex-1 overflow-hidden">
          <!-- Левая панель: инструменты -->
          <aside class="flex w-20 shrink-0 flex-col items-center gap-2 border-r border-gray-700 bg-gray-900/50 py-4">
            <UTooltip text="Карандаш" :ui="{ content: '!z-[9999]' }">
              <UButton
                :color="tool === 'pencil' ? 'primary' : 'neutral'"
                variant="soft"
                size="sm"
                icon="lucide:pencil"
                aria-label="Карандаш"
                @click="setTool('pencil')"
              />
            </UTooltip>
            <UTooltip text="Ластик" :ui="{ content: '!z-[9999]' }">
              <UButton
                :color="tool === 'eraser' ? 'primary' : 'neutral'"
                variant="soft"
                size="sm"
                icon="lucide:eraser"
                aria-label="Ластик"
                @click="setTool('eraser')"
              />
            </UTooltip>
            <UTooltip text="Заливка" :ui="{ content: '!z-[9999]' }">
              <UButton
                :color="tool === 'bucket' ? 'primary' : 'neutral'"
                variant="soft"
                size="sm"
              icon="lucide:paint-bucket"
              aria-label="Заливка"
                @click="setTool('bucket')"
              />
            </UTooltip>
            <UTooltip text="Линия" :ui="{ content: '!z-[9999]' }">
              <UButton
                :color="tool === 'line' ? 'primary' : 'neutral'"
                variant="soft"
                size="sm"
                icon="lucide:minus"
                aria-label="Линия"
                @click="setTool('line')"
              />
            </UTooltip>
            <UTooltip text="Прямоугольник" :ui="{ content: '!z-[9999]' }">
              <UButton
                :color="tool === 'rect' ? 'primary' : 'neutral'"
                variant="soft"
                size="sm"
                icon="lucide:square"
                aria-label="Прямоугольник"
                @click="setTool('rect')"
              />
            </UTooltip>
            <UTooltip text="Круг" :ui="{ content: '!z-[9999]' }">
              <UButton
                :color="tool === 'circle' ? 'primary' : 'neutral'"
                variant="soft"
                size="sm"
                icon="lucide:circle"
                aria-label="Круг"
                @click="setTool('circle')"
              />
            </UTooltip>
          </aside>

          <!-- Холст -->
          <div class="flex min-w-0 flex-1 items-center justify-center overflow-auto p-4">
            <canvas
              ref="canvasEl"
              class="block cursor-crosshair rounded-lg shadow-lg"
              :width="CANVAS_WIDTH"
              :height="CANVAS_HEIGHT"
              style="max-width: 100%; height: auto; touch-action: none"
              @mousedown="onPointerDown"
              @mousemove="onPointerMove"
              @mouseup="onPointerUp"
              @mouseleave="onPointerUp"
              @touchstart.passive="onPointerDown"
              @touchmove.passive="onPointerMove"
              @touchend.passive="onPointerUp"
            />
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
