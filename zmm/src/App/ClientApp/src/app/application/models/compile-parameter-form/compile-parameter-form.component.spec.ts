import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CompileParameterFormComponent } from './compile-parameter-form.component';

describe('CompileParameterFormComponent', () => {
  let component: CompileParameterFormComponent;
  let fixture: ComponentFixture<CompileParameterFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CompileParameterFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CompileParameterFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
