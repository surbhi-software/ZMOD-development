import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TrainingParametersFormComponent } from './training-parameters-form.component';

describe('TrainingParametersFormComponent', () => {
  let component: TrainingParametersFormComponent;
  let fixture: ComponentFixture<TrainingParametersFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TrainingParametersFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TrainingParametersFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
