#lang racket

;; Domain-Specific Language (DSL) for Generating Invoices
;; Tether AI Technologies - DSL Prototype 1
;; File: DSL_1_Invoice.rkt

(define TAX-RATE 0.08)

;; Struct to represent an invoice line item
(struct invoice-item (description price quantity) #:transparent)

;; Function: item
;; Purpose: Constructor for an invoice item within the DSL syntax
(define (item description price quantity)
  (invoice-item description price quantity))

;; Function: invoice
;; Purpose: DSL entry point to process items, compute totals, and print a formatted receipt.
(define (invoice customer-name . items)
  (displayln "==================================================")
  (displayln "          TETHER AI - INVOICE RECEIPT             ")
  (displayln "==================================================")
  (printf "Customer: ~a~n" customer-name)
  (printf "Date:     ~a~n" (date->string (current-date)))
  (displayln "--------------------------------------------------")
  (printf "~a ~a ~a ~a~n"
          (~a "Item Description" #:width 22)
          (~a "Qty" #:width 5 #:align 'right)
          (~a "Price" #:width 9 #:align 'right)
          (~a "Total" #:width 9 #:align 'right))
  (displayln "--------------------------------------------------")

  ;; Process each item imperatively/functionally and accumulate subtotal
  (define subtotal
    (for/fold ([acc-subtotal 0])
              ([it items])
      (define desc (invoice-item-description it))
      (define price (invoice-item-price it))
      (define qty (invoice-item-quantity it))
      (define line-total (* price qty))

      (printf "~a ~a ~a ~a~n"
              (~a desc #:width 22)
              (~a qty #:width 5 #:align 'right)
              (~a (format "$~a" (~r price #:precision '(= 2))) #:width 9 #:align 'right)
              (~a (format "$~a" (~r line-total #:precision '(= 2))) #:width 9 #:align 'right))
      (+ acc-subtotal line-total)))

  (define tax (* subtotal TAX-RATE))
  (define grand-total (+ subtotal tax))

  (displayln "--------------------------------------------------")
  (printf "~a $~a~n" (~a "Subtotal:" #:width 38 #:align 'right) (~r subtotal #:precision '(= 2)))
  (printf "~a $~a~n" (~a "Tax (8%):" #:width 38 #:align 'right) (~r tax #:precision '(= 2)))
  (printf "~a $~a~n" (~a "Grand Total:" #:width 38 #:align 'right) (~r grand-total #:precision '(= 2)))
  (displayln "=================================================="))

;; Helper to format current date string
(require racket/date)
(date-display-format 'iso-date)

;; --- Demonstration / DSL Usage ---
(invoice "Alex Mercer"
         (item "Haircut" 30 2)
         (item "Beard Trim" 15 1)
         (item "Hot Towel Shave" 25 1))
