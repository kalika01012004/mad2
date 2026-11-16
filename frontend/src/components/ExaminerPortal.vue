<template>
  <div class="container-fluid px-3 px-lg-4 py-4">
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="card kpi-card p-3 bg-white">
          <div class="text-muted small">Assigned Examinations</div>
          <h3 class="fw-bold text-primary mb-0">{{ dash.summary.assigned_examinations_count || 0 }}</h3>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card kpi-card p-3 bg-white">
          <div class="text-muted small">Created Slots</div>
          <h3 class="fw-bold text-info mb-0">{{ dash.summary.created_slots_count || 0 }}</h3>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card kpi-card p-3 bg-white">
          <div class="text-muted small">Booked Students</div>
          <h3 class="fw-bold text-success mb-0">{{ dash.summary.booked_students_count || 0 }}</h3>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card kpi-card p-3 bg-white">
          <div class="text-muted small">Pending Evaluations</div>
          <h3 class="fw-bold text-warning mb-0">{{ dash.summary.pending_evaluations_count || 0 }}</h3>
        </div>
      </div>
    </div>

    <ul class="nav nav-pills mb-4 bg-white p-2 rounded-3 shadow-sm">
      <li class="nav-item">
        <button :class="['nav-link', tab === 'dashboard' ? 'active' : '']" @click="tab = 'dashboard'">
          <i class="bi bi-easel me-1"></i>Assigned Examinations
        </button>
      </li>
      <li class="nav-item">
        <button :class="['nav-link', tab === 'slots' ? 'active' : '']" @click="tab = 'slots'">
          <i class="bi bi-calendar-plus me-1"></i>My Slots ({{ (dash.slots || []).length }})
        </button>
      </li>
      <li class="nav-item">
        <button :class="['nav-link', tab === 'evaluations' ? 'active' : '']" @click="tab = 'evaluations'">
          <i class="bi bi-clipboard2-check me-1"></i>Booked Students &amp; Evaluations ({{ (dash.bookings || []).length }})
        </button>
      </li>
    </ul>

    <div v-if="tab === 'dashboard'" class="card section-card p-4">
      <h5 class="fw-bold mb-3">Assigned Examinations</h5>
      <div class="row g-3">
        <div v-for="ex in dash.assigned_examinations" :key="ex.id" class="col-md-6">
          <div class="border rounded-3 p-3 h-100 bg-white">
            <div class="d-flex justify-content-between mb-2">
              <span class="badge bg-dark">{{ ex.course_code }} - {{ ex.course_name }}</span>
              <span class="badge bg-primary">{{ ex.status }}</span>
            </div>
            <h5 class="fw-bold mb-1">{{ ex.name }}</h5>
            <p class="small text-muted mb-2">
              Type: <strong>{{ ex.exam_type }}</strong> | Duration: <strong>{{ ex.duration }} mins</strong> | Max Marks: <strong>{{ ex.max_marks }}</strong>
            </p>
            <div class="small bg-light p-2 rounded mb-3">
              <div><strong>Slot Creation:</strong> {{ ex.slot_creation_start }} to {{ ex.slot_creation_end }}</div>
              <div><strong>Student Booking:</strong> {{ ex.slot_booking_start }} to {{ ex.slot_booking_end }}</div>
            </div>
            <div class="d-flex justify-content-between align-items-center">
              <span :class="['badge', ex.can_create_slots ? 'bg-success' : 'bg-secondary']">
                {{ ex.can_create_slots ? 'Slot Creation Open' : 'Slot Creation Closed' }}
              </span>
              <button
                v-if="ex.can_create_slots"
                class="btn btn-sm btn-primary"
                @click="slotForm.examination_id = ex.id; tab = 'slots'"
              >
                Create Slots
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="tab === 'slots'" class="row g-4">
      <div class="col-lg-4">
        <div class="card section-card p-4">
          <h5 class="fw-bold mb-3">{{ editingSlot ? 'Edit Slot' : 'Add Slot' }}</h5>
          <form @submit.prevent="saveSlot">
            <div class="mb-2">
              <label class="form-label small fw-medium">Examination <span class="text-danger">*</span></label>
              <select class="form-select" v-model="slotForm.examination_id" :disabled="!!editingSlot" required>
                <option v-for="ex in dash.assigned_examinations" :key="ex.id" :value="ex.id">
                  {{ ex.course_code }} - {{ ex.name }} ({{ ex.can_create_slots ? 'Open' : 'Closed' }})
                </option>
              </select>
            </div>
            <div class="mb-2">
              <label class="form-label small fw-medium">Date <span class="text-danger">*</span></label>
              <input type="date" class="form-control" v-model="slotForm.date" required />
            </div>
            <div class="row g-2 mb-2">
              <div class="col-6">
                <label class="form-label small fw-medium">Start Time <span class="text-danger">*</span></label>
                <input type="time" class="form-control" v-model="slotForm.start_time" required />
              </div>
              <div class="col-6">
                <label class="form-label small fw-medium">End Time <span class="text-danger">*</span></label>
                <input type="time" class="form-control" v-model="slotForm.end_time" required />
              </div>
            </div>
            <div class="mb-2">
              <label class="form-label small fw-medium">Max Capacity <span class="text-danger">*</span></label>
              <input type="number" class="form-control" v-model.number="slotForm.max_capacity" min="1" max="50" required />
            </div>
            <div class="mb-2">
              <label class="form-label small fw-medium">Venue</label>
              <input type="text" class="form-control" v-model.trim="slotForm.venue" placeholder="Lab 102 / Google Meet" />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-medium">Meeting Link</label>
              <input type="url" class="form-control" v-model.trim="slotForm.meeting_link" placeholder="https://meet.google.com/..." />
            </div>
            <div class="d-flex gap-2">
              <button type="submit" class="btn btn-primary flex-grow-1">
                {{ editingSlot ? 'Update' : 'Create' }}
              </button>
              <button v-if="editingSlot" type="button" class="btn btn-outline-secondary" @click="resetSlotForm">
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>

      <div class="col-lg-8">
        <div class="card section-card p-4">
          <h5 class="fw-bold mb-3">My Examination Slots ({{ (dash.slots || []).length }})</h5>
          <p class="small text-muted">
            Slots can be edited or removed before student booking begins and while no students are booked.
          </p>
          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr>
                  <th>Examination</th>
                  <th>Date &amp; Time</th>
                  <th>Seats</th>
                  <th>Venue</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in dash.slots" :key="s.id">
                  <td>
                    <span class="badge bg-dark me-1">{{ s.course_code }}</span>
                    <strong>{{ s.examination_name }}</strong>
                  </td>
                  <td>
                    <div>{{ s.date }}</div>
                    <small class="text-muted">{{ s.start_time }} - {{ s.end_time }}</small>
                  </td>
                  <td>
                    <strong>{{ s.available_seats }}</strong> / {{ s.max_capacity }}
                    <small class="text-muted">({{ s.booked_count }} booked)</small>
                  </td>
                  <td class="small">
                    <div>{{ s.venue }}</div>
                    <a v-if="s.meeting_link" :href="s.meeting_link" target="_blank">Meeting Link</a>
                  </td>
                  <td>
                    <span :class="['badge', s.status === 'Available' ? 'bg-success' : s.status === 'Full' ? 'bg-warning text-dark' : 'bg-secondary']">
                      {{ s.status }}
                    </span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-primary" @click="editSlot(s)">
                        <i class="bi bi-pencil"></i>
                      </button>
                      <button class="btn btn-outline-danger" @click="removeSlot(s)">
                        <i class="bi bi-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div v-if="tab === 'evaluations'">
      <div v-if="activeBooking" class="card section-card p-4 mb-4 border-start border-4 border-success">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <div>
            <h5 class="fw-bold mb-0 text-success">
              Evaluate: {{ activeBooking.student_name }} ({{ activeBooking.student_roll_number }})
            </h5>
            <small class="text-muted">
              {{ activeBooking.examination_name }} | Max Marks: <strong>{{ activeBooking.max_marks }}</strong>
            </small>
          </div>
          <button class="btn-close" @click="activeBooking = null"></button>
        </div>

        <form @submit.prevent="saveEvaluation">
          <div v-if="rubricInputs.length > 0" class="table-responsive mb-3">
            <table class="table table-bordered align-middle">
              <thead class="table-light">
                <tr>
                  <th>Criterion</th>
                  <th>Weightage</th>
                  <th>Max Marks</th>
                  <th style="width: 150px;">Marks Awarded *</th>
                  <th>Comment</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in rubricInputs" :key="item.rubric_id">
                  <td>
                    <div class="fw-bold">{{ item.criterion_name }}</div>
                    <small class="text-muted">{{ item.description }}</small>
                  </td>
                  <td>{{ item.weightage }}%</td>
                  <td>{{ item.max_marks }}</td>
                  <td>
                    <input
                      type="number"
                      step="0.5"
                      class="form-control form-control-sm"
                      v-model.number="item.marks_awarded"
                      :max="item.max_marks"
                      min="0"
                      required
                    />
                  </td>
                  <td>
                    <input type="text" class="form-control form-control-sm" v-model="item.comment" />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="mb-3">
            <label class="form-label fw-medium">Total Marks (out of {{ activeBooking.max_marks }})</label>
            <input type="number" step="0.5" class="form-control" v-model.number="directMarks" :max="activeBooking.max_marks" min="0" required />
          </div>

          <div class="row g-3 align-items-center">
            <div class="col-md-8">
              <label class="form-label small fw-medium">Remarks <span class="text-danger">*</span></label>
              <input type="text" class="form-control" v-model.trim="remarks" required />
            </div>
            <div class="col-md-4 text-end">
              <div class="mb-2">
                <span class="text-muted small">Total: </span>
                <span class="fs-5 fw-bold text-primary">{{ calcTotal() }} / {{ activeBooking.max_marks }}</span>
              </div>
              <button type="submit" class="btn btn-success w-100 fw-semibold">
                Save Evaluation
              </button>
            </div>
          </div>
        </form>
      </div>

      <div class="card section-card p-4">
        <h5 class="fw-bold mb-3">Booked Students ({{ (dash.bookings || []).length }})</h5>
        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Student</th>
                <th>Examination</th>
                <th>Date &amp; Time</th>
                <th>Status</th>
                <th>Marks</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="b in dash.bookings" :key="b.id">
                <td>#{{ b.id }}</td>
                <td>
                  <div class="fw-bold">{{ b.student_name }}</div>
                  <small class="text-muted">{{ b.student_roll_number }} | {{ b.student_email }}</small>
                </td>
                <td>
                  <span class="badge bg-dark me-1">{{ b.course_code }}</span>
                  <span>{{ b.examination_name }}</span>
                </td>
                <td>
                  <div>{{ b.slot_date }}</div>
                  <small class="text-muted">{{ b.start_time }} - {{ b.end_time }}</small>
                </td>
                <td>
                  <span :class="['badge', b.status === 'Completed' ? 'bg-success' : 'bg-primary']">{{ b.status }}</span>
                </td>
                <td>
                  <div v-if="b.evaluation">
                    <strong>{{ b.evaluation.total_marks }} / {{ b.max_marks }}</strong>
                    <span class="badge bg-info text-dark ms-1">{{ b.evaluation.grade }}</span>
                    <div class="small text-muted">{{ b.evaluation.remarks }}</div>
                  </div>
                  <span v-else class="badge bg-warning text-dark">Pending</span>
                </td>
                <td>
                  <button class="btn btn-sm btn-primary" @click="startEvaluate(b)">
                    {{ b.evaluation ? 'Edit Marks' : 'Evaluate' }}
                  </button>
                </td>
              </tr>
              <tr v-if="(dash.bookings || []).length === 0">
                <td colspan="7" class="text-center text-muted py-3">No students booked yet.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import EMP_API from "../services/api";

export default {
  name: "ExaminerPortal",
  emits: ["notify"],
  data() {
    const nextWeek = new Date(Date.now() + 5 * 86400000).toISOString().slice(0, 10);
    return {
      tab: "dashboard",
      dash: {
        summary: {},
        assigned_examinations: [],
        slots: [],
        bookings: [],
      },
      editingSlot: null,
      slotForm: {
        examination_id: "",
        date: nextWeek,
        start_time: "10:00",
        end_time: "10:30",
        max_capacity: 2,
        venue: "Online / Google Meet",
        meeting_link: "https://meet.google.com/emp-live-slot",
      },
      activeBooking: null,
      rubricInputs: [],
      remarks: "",
      directMarks: 0,
    };
  },
  mounted() {
    this.fetchDash();
  },
  methods: {
    async fetchDash() {
      try {
        const res = await EMP_API.get("/api/examiner/dashboard");
        this.dash = res;
        if (!this.slotForm.examination_id && res.assigned_examinations && res.assigned_examinations.length > 0) {
          const openEx = res.assigned_examinations.find((e) => e.can_create_slots) || res.assigned_examinations[0];
          this.slotForm.examination_id = openEx.id;
        }
      } catch (err) {
        this.$emit("notify", err.message, "danger");
      }
    },
    resetSlotForm() {
      const nextWeek = new Date(Date.now() + 5 * 86400000).toISOString().slice(0, 10);
      this.editingSlot = null;
      this.slotForm = {
        examination_id:
          this.dash.assigned_examinations.length > 0
            ? this.dash.assigned_examinations[0].id
            : "",
        date: nextWeek,
        start_time: "10:00",
        end_time: "10:30",
        max_capacity: 2,
        venue: "Online / Google Meet",
        meeting_link: "https://meet.google.com/emp-live-slot",
      };
    },
    editSlot(s) {
      this.editingSlot = s;
      this.slotForm = {
        examination_id: s.examination_id,
        date: s.date,
        start_time: s.start_time,
        end_time: s.end_time,
        max_capacity: s.max_capacity,
        venue: s.venue,
        meeting_link: s.meeting_link,
