import { Component, OnInit, ViewChild, Output, EventEmitter, Input } from '@angular/core';

@Component({
  selector: 'app-compile-parameter-form',
  templateUrl: './compile-parameter-form.component.html',
  styleUrls: ['./compile-parameter-form.component.scss']
})
export class CompileParameterFormComponent implements OnInit {

  @Input() showCompileError: any;
  @Output() close = new EventEmitter<any>();
  @Output() selected = new EventEmitter<any>();
  data: any = {};
  formData: any = {};
  public isLoading = false;
  @ViewChild('compileForm') compileForm;
  constructor() { }
  closeForm() {
    this.close.emit(true);
  }
  submit() {
    this.compileForm.submitted = true;
    if (this.compileForm.valid) {
      this.selected.emit(this.formData);
    } else {
    this.showCompileError = true;
    }
  }

  ngOnInit() {
    this.formData = {
      repeat: 10,

    };
  }

}
