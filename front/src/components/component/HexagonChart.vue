<template>
  <div class="hexagon-chart">
    <svg viewBox="-1.2 -1.2 2.4 2.4" width="500" height="500">
      <polygon :points="points" class="hexagon" />
      <polygon :points="dataPoints" class="data" />
      <line v-for="(line, index) in hexagonLines" :key="index" :x1="line.x1" :y1="line.y1" :x2="line.x2" :y2="line.y2" class="hexagon-line" />
      <text v-for="(point, index) in labelPoints" :key="'label' + index" :x="point.x" :y="point.y" class="hexagon-label">{{ labels[index] }}</text>
    </svg>
  </div>
</template>

<script>
export default {
  props: {
    data: {
      type: Array,
      required: true,
    },
    labels: {
      type: Array,
      required: true,
    },
  },
  computed: {
    points() {
      return this.generateHexagonPoints(1).join(' ');
    },
    dataPoints() {
      return this.generateHexagonPoints(0.95, this.data).join(' ');
    },
    hexagonLines() {
      return this.generateHexagonLines(1);
    },
    labelPoints() {
      return this.generateHexagonPoints(1.1).map(point => {
        const [x, y] = point.split(',').map(Number);
        return { x, y:y+0.04 };
      });
    },
  },
  methods: {
    generateHexagonPoints(radius, data = [100, 100, 100, 100, 100, 100]) {
      const angle = Math.PI / 3;
      return data.map((value, index) => {
        const r = radius * value / 100;
        const x = r * Math.cos(angle * index);
        const y = r * Math.sin(angle * index);
        return { x, y };
      }).map(point => `${point.x},${point.y}`);
    },
    generateHexagonLines(radius) {
      const points = this.generateHexagonPoints(radius).map(point => {
        const [x, y] = point.split(',').map(Number);
        return { x, y };
      });
      const lines = [];
      const len = points.length;
      for (let i = 0; i < len; i++) {
        const oppositeIndex = (i + len / 2) % len;
        lines.push({ x1: points[i].x, y1: points[i].y, x2: points[oppositeIndex].x, y2: points[oppositeIndex].y });
      }
      return lines;
    },
  },
};
</script>

<style scoped>
.hexagon {
  fill: none;
  stroke: black;
  stroke-width: 0.03;
}
.data {
  fill: rgba(0, 150, 255, 0.3);
  stroke: rgba(0, 150, 255, 0.7);
  stroke-width: 0.03;
}
.hexagon-line {
  stroke: rgb(10, 9, 9);
  stroke-width: 0.01;
}
.hexagon-label {
  font-size: 0.005em;
  text-anchor: middle;
}
</style>
