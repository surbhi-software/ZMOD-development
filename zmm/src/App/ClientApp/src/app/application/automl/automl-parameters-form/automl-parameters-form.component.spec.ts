import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AutomlParametersFormComponent } from './automl-parameters-form.component';

describe('AutomlParametersFormComponent', () => {
  let component: AutomlParametersFormComponent;
  let fixture: ComponentFixture<AutomlParametersFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AutomlParametersFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AutomlParametersFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
