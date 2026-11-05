# Landing selection and replacement for the custom Selfsteal distribution.
declare -A TEMPLATE_DESCRIPTIONS=(
    [1]="Тёмный кинозал, лаймовый акцент"
    [2]="Светлый сервис, синий, очередь видеоссылок"
    [3]="Киножурнал, сливовый, книжная типографика"
    [4]="Морская панорама, бирюзовый, общий таймлайн"
    [5]="Красная афиша, крупная типографика"
    [6]="Тёплая домашняя страница, бордовый"
    [7]="Контрастный, кислотный, синхронные счётчики"
    [8]="Лавандовый, два экрана, просмотр вдвоём"
    [9]="Лесной пейзаж на весь экран"
    [10]="Мятный дружеский клуб, фотоколлаж"
    [11]="Белый с синим, браузер и очередь видео"
)

show_landing_list() {
    local i
    printf '\nВыберите лендинг:\n\n'
    for i in $(seq 1 11); do
        printf '  %2s) %s — %s\n' "$i" "${TEMPLATE_NAMES[$i]}" "${TEMPLATE_DESCRIPTIONS[$i]}"
    done
    printf '\n   r) Случайный лендинг\n'
}

resolve_landing_choice() {
    local choice="$1"
    case "$choice" in
        random|r|R)
            SELECTED_TEMPLATE=$((RANDOM % 11 + 1))
            ;;
        [1-9]|10|11)
            SELECTED_TEMPLATE="$choice"
            ;;
        *) return 1 ;;
    esac
    printf '\nВыбран: %s (%s)\n' "${TEMPLATE_NAMES[$SELECTED_TEMPLATE]}" "$SELECTED_TEMPLATE"
}

select_install_template() {
    local choice
    if [ -n "${FORCE_TEMPLATE:-}" ]; then
        resolve_landing_choice "$FORCE_TEMPLATE"
        return $?
    fi
    if [ "${FORCE_MODE:-false}" = true ]; then
        log_error "В режиме --force укажите --template 1..11 или --template random."
        return 1
    fi
    show_landing_list
    printf '   0) Отменить установку\n\n'
    while true; do
        if ! read -r -p 'Номер лендинга [1–11], r — случайный, 0 — отмена: ' choice; then
            log_error "Выбор не получен. Укажите --template 1..11 или --template random."
            return 1
        fi
        if [ "$choice" = 0 ]; then
            printf 'Установка отменена.\n'
            return 1
        fi
        if resolve_landing_choice "$choice"; then return 0; fi
        printf 'Введите номер от 1 до 11 или r.\n'
    done
}

show_template_options() {
    show_landing_list
    printf '   v) Посмотреть текущий лендинг\n   k) Оставить текущий\n   0) Выйти\n\n'
}

replace_selected_template() {
    local template_id="$1"
    if ! download_template "$template_id"; then return 1; fi
    # Adopt this custom manager even when the existing install used upstream.
    if ! install_management_script; then
        log_error "Лендинг заменён, но управляющую команду обновить не удалось."
        return 1
    fi
    printf '\nЛендинг заменён: %s\n' "${TEMPLATE_NAMES[$template_id]}"
    printf 'Резервная копия сохранена. Перезапуск веб-сервера не требуется.\n'
}

template_command() {
    check_running_as_root
    if [ ! -f "$APP_DIR/docker-compose.yml" ] || [ ! -d "$HTML_DIR" ]; then
        log_error "Установка Selfsteal не найдена. Сначала выполните install."
        return 1
    fi
    if [ -n "${FORCE_TEMPLATE:-}" ]; then
        resolve_landing_choice "$FORCE_TEMPLATE" || return 1
        replace_selected_template "$SELECTED_TEMPLATE"
        return $?
    fi
    local choice
    while true; do
        show_template_options
        if ! read -r -p 'Лендинг [1–11], r, v, k или 0: ' choice; then
            log_error "Выбор не получен. Для замены укажите --template 1..11 или random."
            return 1
        fi
        case "$choice" in
            0|k|K) return 0 ;;
            v|V) show_current_template_info ;;
            *)
                if resolve_landing_choice "$choice"; then
                    replace_selected_template "$SELECTED_TEMPLATE"
                    return $?
                fi
                printf 'Введите номер от 1 до 11, r, v, k или 0.\n'
                ;;
        esac
    done
}
