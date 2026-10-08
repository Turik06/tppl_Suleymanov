section   .text
global    main
default   rel
extern    printf

BUFFER_SIZE equ 65536

main:
        push  rbp
        mov   rbp, rsp
        push  rbx
        push  r12

        cmp   rdi, 2
        jl    no_args

        mov   rax, [rsi + 8]
        mov   [filename], rax

        ; --- Открытие файла (sys_open, шаблон из contex/read-file.asm) ---
        mov   rax, 2
        mov   rdi, [filename]
        xor   rsi, rsi
        xor   rdx, rdx
        syscall
        test  rax, rax
        js    open_error
        mov   [fd], rax

        ; --- Чтение файла в буфер (sys_read, шаблон из contex/read-file.asm) ---
        mov   rax, 0
        mov   rdi, [fd]
        mov   rsi, buffer
        mov   rdx, BUFFER_SIZE
        syscall
        test  rax, rax
        jle   read_error
        mov   [bytes_read], rax

        ; --- Закрытие файла (sys_close, шаблон из contex/read-file.asm) ---
        mov   rax, 3
        mov   rdi, [fd]
        syscall

        ; --- Разбор строк на лету без массивов (алгоритм от товарища) ---
        mov   rsi, buffer               ; rsi = начало данных
        mov   rdi, buffer
        add   rdi, [bytes_read]         ; rdi = конец прочитанных данных

        call  parse_line                ; первая строка (x)
        jc    format_error
        mov   rbx, rax                  ; rbx = сумма x
        mov   r12, rcx                  ; r12 = количество чисел x

        call  parse_line                ; вторая строка (y); rsi уже указывает на её начало
        jc    format_error
        cmp   rcx, r12                  ; количество чисел должно совпадать
        jne   format_error
        sub   rbx, rax                  ; rbx = (сумма x) - (сумма y) = сумма разностей

        ; Проверяем хвост файла: допустимы только пробелы, табы и переносы строк
.trail:
        cmp   rsi, rdi
        jae   .compute
        mov   r10b, [rsi]
        inc   rsi
        cmp   r10b, ' '
        je    .trail
        cmp   r10b, 9
        je    .trail
        cmp   r10b, 10
        je    .trail
        cmp   r10b, 13
        je    .trail
        jmp   format_error

.compute:
        mov   rax, rbx                  ; делимое = сумма разностей
        cqo                             ; знаковое расширение rax в rdx:rax
        idiv  r12                       ; rax = среднее = sum / count

        ; --- Вывод результата через printf (из contex/printf-example.asm) ---
        mov   rdi, fmt_result
        mov   rsi, [filename]
        mov   rdx, rax
        xor   rax, rax
        call  printf

        pop   r12
        pop   rbx
        pop   rbp
        xor   eax, eax
        ret

read_error:
        mov   rax, 3                    ; sys_close перед выходом
        mov   rdi, [fd]
        syscall

open_error:
format_error:
        mov   rdi, fmt_error
        mov   rsi, [filename]
        xor   rax, rax
        call  printf

        pop   r12
        pop   rbx
        pop   rbp
        mov   eax, 1
        ret

no_args:
        mov   rdi, fmt_usage
        xor   rax, rax
        call  printf

        pop   r12
        pop   rbx
        pop   rbp
        mov   eax, 1
        ret

; ---------------------------------------------------------------------------
; skip_ws: пропускает пробелы, табы и '\r' (но не '\n': это конец строки)
;   вход:  rsi = текущая позиция, rdi = конец данных
;   выход: rsi сдвинут на первый непробельный символ (или равен rdi)
;   портит: r10
skip_ws:
.loop:
        cmp   rsi, rdi
        jae   .done
        mov   r10b, [rsi]
        cmp   r10b, ' '
        je    .skip
        cmp   r10b, 9
        je    .skip
        cmp   r10b, 13
        jne   .done
.skip:
        inc   rsi
        jmp   .loop
.done:
        ret

; ---------------------------------------------------------------------------
; parse_line: разбирает одну строку чисел через запятую на лету
;   вход:  rsi = начало строки, rdi = конец данных
;   выход: rax = сумма чисел, rcx = сколько чисел, rsi = позиция после '\n'
;          CF = 1 при ошибке (иначе CF = 0)
;   портит: rdx, r8, r9, r10
parse_line:
        xor   rax, rax                  ; rax = сумма чисел
        xor   rcx, rcx                  ; rcx = количество чисел

.next_number:
        call  skip_ws
        cmp   rsi, rdi
        jae   .error                    ; ждали число, но данные закончились

        xor   r8, r8                    ; r8 = 1 если число отрицательное
        cmp   byte [rsi], '-'
        jne   .check_plus
        mov   r8, 1
        inc   rsi
        jmp   .digits

.check_plus:
        cmp   byte [rsi], '+'
        jne   .digits
        inc   rsi

.digits:
        xor   rdx, rdx                  ; rdx = значение числа
        xor   r9, r9                    ; r9 = количество цифр
.digit_loop:
        cmp   rsi, rdi
        jae   .digits_done
        movzx r10, byte [rsi]
        sub   r10, '0'
        cmp   r10, 9
        ja    .digits_done
        imul  rdx, rdx, 10
        add   rdx, r10
        inc   rsi
        inc   r9
        jmp   .digit_loop

.digits_done:
        test  r9, r9                    ; была хотя бы одна цифра?
        jz    .error
        test  r8, r8
        jz    .add
        neg   rdx

.add:
        add   rax, rdx                  ; прибавляем к общей сумме
        inc   rcx                       ; считаем число
        call  skip_ws
        cmp   rsi, rdi
        jae   .ok                       ; конец файла без '\n'

        mov   r10b, [rsi]
        inc   rsi
        cmp   r10b, ','
        je    .next_number
        cmp   r10b, 10                  ; '\n'
        je    .ok

.error:
        stc
        ret

.ok:
        clc
        ret

; ---------------------------------------------------------------------------
section   .data
        fmt_result  db "%s: %ld", 10, 0
        fmt_error   db "%s: файл испорчен", 10, 0
        fmt_usage   db "Usage: ./average <filename>", 10, 0

section   .bss
        fd          resq 1
        filename    resq 1
        bytes_read  resq 1
        buffer      resb BUFFER_SIZE
