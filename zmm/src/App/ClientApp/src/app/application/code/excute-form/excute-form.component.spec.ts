import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ExcuteFormComponent } from './excute-form.component';

describe('ExcuteFormComponent', () => {
  let component: ExcuteFormComponent;
  let fixture: ComponentFixture<ExcuteFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ExcuteFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ExcuteFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
