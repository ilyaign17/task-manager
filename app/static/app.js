// =====================
// Tabs (переключение панелей без перезагрузки)
// =====================

/** Панели по ключу вкладки */
const panels = {
  task: document.getElementById("tab-task"),
  list: document.getElementById("tab-list"),
};

/** Переключение таба */
function switchTab(key) {
  // Активируем кнопку
  document.querySelectorAll(".tab").forEach((b) =>
    b.classList.toggle("active", b.dataset.tab === key)
  );

  // Показываем нужную панель
  Object.entries(panels).forEach(([k, el]) =>
    el.classList.toggle("hidden", k !== key)
  );

  if (key === "list") refreshList();
}

// Назначаем обработчики
document.querySelectorAll(".tab").forEach((btn) =>
  btn.addEventListener("click", () => switchTab(btn.dataset.tab))
);

// =====================
// DOM-элементы
// =====================
const form = document.getElementById("task-form");
const uuidHidden = document.getElementById("task-uuid");
const titleInput = document.getElementById("task-title");
const descInput = document.getElementById("task-desc");
const statusSelect = document.getElementById("task-status");
const uuidLine = document.getElementById("uuid-line");
const uuidText = document.getElementById("uuid-text");

const saveBtn = document.getElementById("btn-save");
const resetBtn = document.getElementById("btn-reset");

const quickUuid = document.getElementById("quick-uuid");
const quickBtn = document.getElementById("btn-fetch-by-uuid");
const quickErr = document.getElementById("quick-error");

const filterStatus = document.getElementById("filter-status");
const refreshBtn = document.getElementById("btn-refresh");
const newBtn = document.getElementById("btn-new");
const listContainer = document.getElementById("list-container");

// =====================
// Утилиты
// =====================

/**
 * Заполнить форму данными задачи или очистить.
 * @param {object|null} data — объект задачи или null для сброса
 */
function setForm(data) {
  uuidHidden.value = data?.uuid || "";
  titleInput.value = data?.title || "";
  descInput.value = data?.description || "";
  statusSelect.value = data?.status || "создано";

  if (data?.uuid) {
    uuidText.textContent = data.uuid;
    uuidLine.hidden = false;
  } else {
    uuidText.textContent = "";
    uuidLine.hidden = true;
  }
}

/** Показ простого алерта об ошибке */
function toastError(err) {
  alert(err);
}

// =====================
// Сабмит формы (Создать / Обновить)
// =====================
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = {
    title: titleInput.value.trim(),
    description: (descInput.value || "").trim() || null,
    status: statusSelect.value,
  };

  if (!payload.title) return toastError("Заполните заголовок");

  try {
    const uuid = uuidHidden.value;
    let res;

    if (uuid && saveBtn.disabled) {
      return toastError("Сохранение заблокировано. Нажмите «Сбросить форму».");
    }

    // Создание или обновление
    res = await fetch(`/tasks${uuid ? `/${uuid}` : ""}`, {
      method: uuid ? "PATCH" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error((await res.text()) || "Ошибка сохранения");

    setForm(null);
    saveBtn.disabled = false;
    saveBtn.removeAttribute("title");

    if (!panels.list.classList.contains("hidden")) refreshList();
  } catch (e2) {
    toastError(e2.message);
  }
});

// Сброс формы
resetBtn.addEventListener("click", () => {
  setForm(null);
  saveBtn.disabled = false;
  saveBtn.removeAttribute("title");
});

// =====================
// Быстрый доступ по UUID
// =====================
quickBtn.addEventListener("click", async () => {
  quickErr.hidden = true;
  const id = (quickUuid.value || "").trim();
  if (!id) return;

  saveBtn.disabled = true;
  saveBtn.title =
    "Кнопка заблокирована. Нажмите «Сбросить форму», чтобы снова редактировать.";

  try {
    const res = await fetch(`/tasks/${id}`);
    if (!res.ok) {
      quickErr.textContent = "Задача с таким UUID не найдена";
      quickErr.hidden = false;
      saveBtn.disabled = false;
      saveBtn.removeAttribute("title");
      return;
    }

    setForm(await res.json());
    switchTab("task");
  } catch (e) {
    quickErr.textContent = e.message;
    quickErr.hidden = false;
    saveBtn.disabled = false;
    saveBtn.removeAttribute("title");
  }
});

// =====================
// Список задач
// =====================
async function refreshList() {
  try {
    const params = new URLSearchParams();
    if (filterStatus.value) params.set("status", filterStatus.value);

    const res = await fetch(`/tasks?${params.toString()}`);
    if (!res.ok) throw new Error((await res.text()) || "Ошибка получения списка");

    const list = await res.json();
    listContainer.innerHTML = "";

    if (!list.length) {
      const empty = document.createElement("div");
      empty.className = "card";
      empty.textContent = "Задач нет.";
      return listContainer.appendChild(empty);
    }

    list.forEach((item) => {
      const row = document.createElement("div");
      row.className = "task-row";

      // Заголовок
      const head = document.createElement("div");
      head.className = "task-head";

      const left = document.createElement("div");

      const title = document.createElement("div");
      title.className = "task-title";
      title.textContent = item.title;

      const aux = document.createElement("div");
      aux.className = "task-aux";

      const pill = document.createElement("span");
      pill.className = "pill";
      pill.textContent = item.status;

      const uuid = document.createElement("span");
      uuid.textContent = `UUID: ${item.uuid}`;

      aux.append(pill, uuid);
      left.append(title, aux);

      // Действия
      const actions = document.createElement("div");
      actions.className = "task-actions";

      const edit = document.createElement("button");
      edit.className = "ghost";
      edit.textContent = "Редактировать";
      edit.addEventListener("click", () => {
        setForm(item);
        saveBtn.disabled = false;
        saveBtn.removeAttribute("title");
        switchTab("task");
      });

      const del = document.createElement("button");
      del.className = "secondary";
      del.textContent = "Удалить";
      del.addEventListener("click", async () => {
        if (!confirm("Удалить задачу?")) return;
        const r = await fetch(`/tasks/${item.uuid}`, { method: "DELETE" });
        r.status === 204 ? refreshList() : toastError("Ошибка удаления");
      });

      actions.append(edit, del);
      head.append(left, actions);

      // Детали
      const details = document.createElement("div");
      details.className = "task-details";
      details.textContent = item.description || "—";
      title.addEventListener("click", () => details.classList.toggle("open"));

      row.append(head, details);
      listContainer.appendChild(row);
    });
  } catch (e) {
    toastError(e.message);
  }
}

// Кнопки управления списком
refreshBtn.addEventListener("click", refreshList);
filterStatus.addEventListener("change", refreshList);
newBtn.addEventListener("click", () => {
  setForm(null);
  saveBtn.disabled = false;
  saveBtn.removeAttribute("title");
  switchTab("task");
});

// Начальная подгрузка
refreshList();
