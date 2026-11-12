<template>
  <div
    class="modal fade show d-block"
    tabindex="-1"
    style="background: rgba(15, 23, 42, 0.55);"
  >
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content border-0 shadow">
        <div class="modal-header bg-primary text-white">
          <h5 class="modal-title fw-bold">Profile Settings</h5>
          <button type="button" class="btn-close btn-close-white" @click="$emit('close')"></button>
        </div>
        <form @submit.prevent="save">
          <div class="modal-body">
            <div class="mb-2">
              <label class="form-label small fw-medium">Full Name *</label>
              <input type="text" class="form-control" v-model.trim="form.name" required />
            </div>
            <div class="row g-2 mb-2">
              <div class="col-6">
                <label class="form-label small fw-medium">Department</label>
                <input type="text" class="form-control" v-model.trim="form.department" />
              </div>
              <div class="col-6">
                <label class="form-label small fw-medium">Contact Number</label>
                <input type="text" class="form-control" v-model.trim="form.contact_details" />
              </div>
            </div>
            <div v-if="user.role === 'student'" class="mb-2">
              <label class="form-label small fw-medium">Roll Number</label>
              <input type="text" class="form-control" v-model.trim="form.roll_number" />
            </div>
            <div v-if="user.role === 'examiner'" class="mb-2">
              <label class="form-label small fw-medium">Specialization</label>
              <input type="text" class="form-control" v-model.trim="form.specialization" />
            </div>
            <div class="mb-2">
              <label class="form-label small fw-medium">Google Chat Webhook URL</label>
              <input type="url" class="form-control" v-model.trim="form.gchat_webhook" placeholder="https://chat.googleapis.com/v1/spaces/..." />
            </div>
            <div class="mb-2">
              <label class="form-label small fw-medium">New Password</label>
              <input type="password" class="form-control" v-model="form.new_password" minlength="6" />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" @click="$emit('close')">Cancel</button>
            <button type="submit" class="btn btn-primary">Save</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import EMP_API from "../services/api";

export default {
  name: "ProfileModal",
  props: {
    user: { type: Object, required: true },
  },
