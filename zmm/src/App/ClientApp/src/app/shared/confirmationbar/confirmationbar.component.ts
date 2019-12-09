import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-confirmationbar',
  templateUrl: './confirmationbar.component.html',
  styleUrls: ['./confirmationbar.component.scss']
})
export class ConfirmationbarComponent implements OnInit {

  @Input() message: string;
  @Output() confirmDelete = new EventEmitter<any>();
  displayConfirmationbar = false;
  constructor() { }

  ngOnInit() {
  }
  deleteData(args: any): void {
    this.confirmDelete.emit(args);
    this.displayConfirmationbar = false;
  }
}
