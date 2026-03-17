{{/*
Expand the name of the chart.
*/}}
{{- define "todo-chatbot.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-chatbot.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "todo-chatbot.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-chatbot.labels" -}}
helm.sh/chart: {{ include "todo-chatbot.chart" . }}
{{ include "todo-chatbot.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-chatbot.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-chatbot.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "todo-chatbot.frontend.labels" -}}
{{ include "todo-chatbot.labels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "todo-chatbot.frontend.selectorLabels" -}}
{{ include "todo-chatbot.selectorLabels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Backend labels
*/}}
{{- define "todo-chatbot.backend.labels" -}}
{{ include "todo-chatbot.labels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "todo-chatbot.backend.selectorLabels" -}}
{{ include "todo-chatbot.selectorLabels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Reminder service labels
*/}}
{{- define "todo-chatbot.reminder.labels" -}}
{{ include "todo-chatbot.labels" . }}
app.kubernetes.io/component: reminder
{{- end }}

{{/*
Reminder service selector labels
*/}}
{{- define "todo-chatbot.reminder.selectorLabels" -}}
{{ include "todo-chatbot.selectorLabels" . }}
app.kubernetes.io/component: reminder
{{- end }}

{{/*
Recurring service labels
*/}}
{{- define "todo-chatbot.recurring.labels" -}}
{{ include "todo-chatbot.labels" . }}
app.kubernetes.io/component: recurring
{{- end }}

{{/*
Recurring service selector labels
*/}}
{{- define "todo-chatbot.recurring.selectorLabels" -}}
{{ include "todo-chatbot.selectorLabels" . }}
app.kubernetes.io/component: recurring
{{- end }}

{{/*
Sync service labels
*/}}
{{- define "todo-chatbot.sync.labels" -}}
{{ include "todo-chatbot.labels" . }}
app.kubernetes.io/component: sync
{{- end }}

{{/*
Sync service selector labels
*/}}
{{- define "todo-chatbot.sync.selectorLabels" -}}
{{ include "todo-chatbot.selectorLabels" . }}
app.kubernetes.io/component: sync
{{- end }}

{{/*
Redpanda labels
*/}}
{{- define "todo-chatbot.redpanda.labels" -}}
{{ include "todo-chatbot.labels" . }}
app.kubernetes.io/component: redpanda
{{- end }}

{{/*
Redpanda selector labels
*/}}
{{- define "todo-chatbot.redpanda.selectorLabels" -}}
{{ include "todo-chatbot.selectorLabels" . }}
app.kubernetes.io/component: redpanda
{{- end }}
